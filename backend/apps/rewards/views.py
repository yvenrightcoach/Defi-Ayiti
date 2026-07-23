"""Vues DRF de l'app 'rewards'."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.accounts.models import UserProfile

from .models import Achievement, Mission, PlayerAchievement, PlayerMission, Purchase, Reward, ShopItem
from .serializers import (
    AchievementSerializer,
    ClaimMissionResultSerializer,
    CreatePurchaseSerializer,
    MissionSerializer,
    PlayerAchievementSerializer,
    PlayerMissionSerializer,
    PurchaseSerializer,
    RewardSerializer,
    ShopItemSerializer,
)


class RewardViewSet(viewsets.ReadOnlyModelViewSet):
    """Catalogue des recompenses (coffres, badges, avatars, cadres...)."""

    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    filterset_fields = ["reward_type"]


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """Catalogue des achievements/badges disponibles."""

    queryset = Achievement.objects.select_related("reward").all()
    serializer_class = AchievementSerializer


class PlayerAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """Progression et deblocage des achievements pour le joueur connecte."""

    serializer_class = PlayerAchievementSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return PlayerAchievement.objects.none()
        return PlayerAchievement.objects.filter(profile__user=self.request.user).select_related(
            "achievement__reward"
        )


class MissionViewSet(viewsets.ReadOnlyModelViewSet):
    """Catalogue des missions (quetes quotidiennes)."""

    queryset = Mission.objects.filter(is_active=True)
    serializer_class = MissionSerializer


class PlayerMissionViewSet(viewsets.ReadOnlyModelViewSet):
    """Quetes du jour assignees au joueur connecte, avec reclamation de recompense."""

    serializer_class = PlayerMissionSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return PlayerMission.objects.none()
        return PlayerMission.objects.filter(profile__user=self.request.user).select_related("mission")

    @action(detail=True, methods=["post"])
    def claim(self, request, pk=None):
        """Reclame la recompense d'une quete terminee (une seule fois)."""
        player_mission = self.get_object()
        if not player_mission.is_completed:
            raise ValidationError("Cette quete n'est pas encore terminee.")
        if player_mission.reward_claimed:
            raise ValidationError("La recompense de cette quete a deja ete reclamee.")

        profile = player_mission.profile
        profile.add_xp(player_mission.mission.xp_reward)
        profile.coins += player_mission.mission.coin_reward
        profile.save(update_fields=["coins"])

        player_mission.reward_claimed = True
        player_mission.save(update_fields=["reward_claimed"])

        result = ClaimMissionResultSerializer(
            {"xp_awarded": player_mission.mission.xp_reward, "coin_awarded": player_mission.mission.coin_reward}
        )
        return Response(result.data)


class ShopItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Boutique : avatars, cadres de profil et boosters achetables."""

    queryset = ShopItem.objects.filter(is_available=True)
    serializer_class = ShopItemSerializer
    filterset_fields = ["item_type"]


class PurchaseViewSet(viewsets.ModelViewSet):
    """Historique d'achats du joueur connecte + action d'achat."""

    http_method_names = ["get", "post", "head", "options"]
    serializer_class = PurchaseSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Purchase.objects.none()
        return Purchase.objects.filter(profile__user=self.request.user).select_related("shop_item")

    def create(self, request, *args, **kwargs):
        payload = CreatePurchaseSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        shop_item = payload.validated_data["shop_item_id"]

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if profile.coins < shop_item.price_coins or profile.diamonds < shop_item.price_diamonds:
            raise ValidationError("Solde insuffisant pour cet achat.")

        profile.coins -= shop_item.price_coins
        profile.diamonds -= shop_item.price_diamonds
        if shop_item.item_type == "avatar":
            profile.avatar_url = shop_item.image
        profile.save(update_fields=["coins", "diamonds", "avatar_url"])

        purchase = Purchase.objects.create(
            profile=profile,
            shop_item=shop_item,
            price_paid_coins=shop_item.price_coins,
            price_paid_diamonds=shop_item.price_diamonds,
        )
        return Response(PurchaseSerializer(purchase).data, status=201)
