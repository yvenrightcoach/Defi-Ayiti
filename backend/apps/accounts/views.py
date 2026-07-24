"""Vues DRF de l'app 'accounts'."""
import uuid

from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserProfile
from .serializers import GuestLoginResponseSerializer, UserProfileSerializer, UserProfileUpdateSerializer


class GuestLoginView(APIView):
    """
    Cree un compte invite temporaire et retourne directement une paire de
    jetons JWT, sans mot de passe. Permet de jouer sans creer de compte.
    """

    permission_classes = [AllowAny]
    throttle_scope = "auth"

    @extend_schema(request=None, responses=GuestLoginResponseSerializer)
    def post(self, request, *args, **kwargs):
        if not settings.GUEST_MODE_ENABLED:
            return Response({"detail": "Le mode invite est desactive."}, status=403)

        suffix = uuid.uuid4().hex[:10]
        guest = User.objects.create_user(
            username=f"invite_{suffix}",
            email=f"invite_{suffix}@guest.defi-ayiti.local",
            is_guest=True,
        )
        guest.set_unusable_password()
        guest.save(update_fields=["password"])

        refresh = RefreshToken.for_user(guest)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": str(guest.id),
                    "username": guest.username,
                    "is_guest": guest.is_guest,
                },
            },
            status=201,
        )


class MeProfileView(RetrieveUpdateAPIView):
    """Profil de jeu de l'utilisateur connecte (GET/PATCH /accounts/me/)."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return UserProfileUpdateSerializer
        return UserProfileSerializer

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class ClaimAdRewardView(APIView):
    """
    Accorde un bonus de pieces apres visionnage d'une pub recompensee cote
    client (voir frontend/src/lib/ads.ts). Plafonne a AD_REWARD_DAILY_LIMIT
    par jour ; c'est la seule protection anti-abus tant qu'aucune
    verification serveur-a-serveur du reseau publicitaire n'est branchee
    (a activer avec un vrai compte AdMob/Ad Manager en production).
    """

    permission_classes = [IsAuthenticated]
    throttle_scope = "ad_reward"

    AD_REWARD_AMOUNT = 30
    AD_REWARD_DAILY_LIMIT = 5

    def post(self, request, *args, **kwargs):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        awarded = profile.claim_ad_reward(amount=self.AD_REWARD_AMOUNT, daily_limit=self.AD_REWARD_DAILY_LIMIT)
        if awarded is None:
            return Response(
                {"detail": "Limite quotidienne de recompenses publicitaires atteinte.", "coins_awarded": 0, "coins": profile.coins},
                status=429,
            )
        return Response({"coins_awarded": awarded, "coins": profile.coins})


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Consultation publique (authentifiee) du profil d'un autre joueur.
    Filtrer par ?search=<username> pour retrouver un joueur (ajout d'ami).
    """

    queryset = UserProfile.objects.select_related("user", "department").all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(user__username__icontains=search)
        return queryset
