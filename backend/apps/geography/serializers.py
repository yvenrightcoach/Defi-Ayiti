"""Serializers DRF de l'app 'geography'."""
from rest_framework import serializers

from .models import Department, Level


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = (
            "id", "department", "order", "name", "description", "question_count",
            "required_score", "xp_reward", "coin_reward", "is_boss_level", "unlocks_hero",
        )


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = (
            "id", "name", "slug", "code", "capital", "description",
            "map_image", "icon", "boss_name", "order",
        )


class DepartmentDetailSerializer(DepartmentSerializer):
    """Departement avec la liste de ses chapitres (utilise sur /geography/departments/{id}/)."""

    levels = LevelSerializer(many=True, read_only=True)

    class Meta(DepartmentSerializer.Meta):
        fields = DepartmentSerializer.Meta.fields + ("levels",)
