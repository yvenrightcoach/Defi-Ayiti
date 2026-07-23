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
