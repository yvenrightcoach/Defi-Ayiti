"""Vues DRF de l'app 'payments'."""
import stripe
from django.conf import settings
from rest_framework import viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserProfile

from .models import DiamondPack, DiamondPurchase, PaymentProvider, PaymentStatus
from .serializers import CheckoutSessionSerializer, CreateCheckoutSerializer, DiamondPackSerializer


class DiamondPackViewSet(viewsets.ReadOnlyModelViewSet):
    """Catalogue des packs de diamants disponibles a l'achat."""

    serializer_class = DiamondPackSerializer
    queryset = DiamondPack.objects.filter(is_active=True)


class CreateStripeCheckoutView(APIView):
    """Cree une session Stripe Checkout pour l'achat d'un pack de diamants."""

    permission_classes = [IsAuthenticated]
    throttle_scope = "payments"

    def post(self, request, *args, **kwargs):
        payload = CreateCheckoutSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        try:
            pack = DiamondPack.objects.get(id=payload.validated_data["pack_id"], is_active=True)
        except DiamondPack.DoesNotExist as exc:
            raise NotFound("Pack de diamants introuvable.") from exc

        if not settings.STRIPE_SECRET_KEY:
            raise ValidationError("Les paiements ne sont pas encore configures.")

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY

        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": f"Defi Ayiti - {pack.name}"},
                        "unit_amount": pack.price_usd_cents,
                    },
                    "quantity": 1,
                }
            ],
            success_url=f"{settings.FRONTEND_URL}/profil?paiement=succes",
            cancel_url=f"{settings.FRONTEND_URL}/profil?paiement=annule",
            client_reference_id=str(profile.id),
            metadata={"profile_id": str(profile.id), "pack_id": str(pack.id)},
        )

        DiamondPurchase.objects.create(
            profile=profile,
            pack=pack,
            provider=PaymentProvider.STRIPE,
            provider_reference=session.id,
        )

        return Response(CheckoutSessionSerializer({"checkout_url": session.url}).data)


class StripeWebhookView(APIView):
    """
    Recoit les evenements Stripe. Seule source de verite pour crediter des
    diamants : le retour navigateur (success_url) n'est jamais suffisant, il
    peut etre visite sans paiement reel.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        try:
            event = stripe.Webhook.construct_event(request.body, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError):
            return Response(status=400)

        if event["type"] == "checkout.session.completed":
            self._credit_purchase(event["data"]["object"]["id"])

        return Response(status=200)

    @staticmethod
    def _credit_purchase(session_id: str) -> None:
        try:
            purchase = DiamondPurchase.objects.select_related("profile", "pack").get(provider_reference=session_id)
        except DiamondPurchase.DoesNotExist:
            return
        if purchase.diamonds_credited:
            return

        purchase.status = PaymentStatus.PAID
        purchase.diamonds_credited = True
        purchase.save(update_fields=["status", "diamonds_credited"])

        profile = purchase.profile
        profile.diamonds += purchase.pack.diamonds_amount
        profile.save(update_fields=["diamonds"])
