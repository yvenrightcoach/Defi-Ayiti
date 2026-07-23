"""Serializers DRF de l'app 'heroes'."""
from rest_framework import serializers

from .models import Hero, HeroCard


class HeroSerializer(serializers.ModelSerializer):
    """Catalogue des heros, avec 'is_unlocked' calcule pour le joueur connecte."""

    is_unlocked = serializers.SerializerMethodField()

    class Meta:
        model = Hero
        fields = (
            "id", "name", "slug", "image", "card_image", "biography", "quote",
            "department", "unlock_level", "rarity", "order", "is_unlocked",
        )

    def get_is_unlocked(self, obj) -> bool:
        profile = self.context.get("profile")
        if profile is None:
            return False
        return obj.cards.filter(profile=profile).exists()


class HeroCardSerializer(serializers.ModelSerializer):
    hero = HeroSerializer(read_only=True)

    class Meta:
        model = HeroCard
        fields = ("id", "hero", "unlocked_at", "unlocked_via_level")
        read_only_fields = fields
