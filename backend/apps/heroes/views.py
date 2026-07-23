"""Vues DRF de l'app 'heroes'."""
from rest_framework import viewsets

from apps.accounts.models import UserProfile

from .models import Hero, HeroCard
from .serializers import HeroCardSerializer, HeroSerializer


class HeroViewSet(viewsets.ReadOnlyModelViewSet):
    """Catalogue complet des heros historiques, avec statut de deblocage du joueur connecte."""

    queryset = Hero.objects.select_related("department").all()
    serializer_class = HeroSerializer
    filterset_fields = ["department", "rarity"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["profile"] = UserProfile.objects.filter(user=self.request.user).first()
        return context


class HeroCardViewSet(viewsets.ReadOnlyModelViewSet):
    """Collection de heros debloques par le joueur connecte."""

    serializer_class = HeroCardSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return HeroCard.objects.none()
        return HeroCard.objects.filter(profile__user=self.request.user).select_related("hero")
