"""Serializers DRF de l'app 'rewards'."""
from rest_framework import serializers

from .models import (
    Achievement,
    Mission,
    PlayerAchievement,
    PlayerMission,
    Purchase,
    Reward,
    ShopItem,
)


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = (
            "id", "name", "description", "reward_type", "image",
            "coins_amount", "diamonds_amount", "xp_amount", "grants_hero",
        )


class AchievementSerializer(serializers.ModelSerializer):
    reward = RewardSerializer(read_only=True)

    class Meta:
        model = Achievement
        fields = ("id", "name", "description", "icon", "criteria_type", "criteria_value", "reward")


class PlayerAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = PlayerAchievement
        fields = ("id", "achievement", "progress", "unlocked_at")
        read_only_fields = fields


class MissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = (
            "id", "name", "description", "mission_type", "target_value",
            "xp_reward", "coin_reward", "is_daily", "is_active",
        )


class PlayerMissionSerializer(serializers.ModelSerializer):
    mission = MissionSerializer(read_only=True)

    class Meta:
        model = PlayerMission
        fields = (
            "id", "mission", "assigned_date", "progress",
            "is_completed", "completed_at", "reward_claimed",
        )
        read_only_fields = fields


class ClaimMissionResultSerializer(serializers.Serializer):
    xp_awarded = serializers.IntegerField()
    coin_awarded = serializers.IntegerField()


class ShopItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopItem
        fields = ("id", "name", "description", "item_type", "image", "price_coins", "price_diamonds", "is_available")


class PurchaseSerializer(serializers.ModelSerializer):
    shop_item = ShopItemSerializer(read_only=True)

    class Meta:
        model = Purchase
        fields = ("id", "shop_item", "price_paid_coins", "price_paid_diamonds", "purchased_at")
        read_only_fields = fields


class CreatePurchaseSerializer(serializers.Serializer):
    shop_item_id = serializers.PrimaryKeyRelatedField(queryset=ShopItem.objects.filter(is_available=True))
