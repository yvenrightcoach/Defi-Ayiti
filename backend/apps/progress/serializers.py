"""Serializers DRF de l'app 'progress'."""
from rest_framework import serializers

from apps.geography.serializers import DepartmentSerializer, LevelSerializer
from apps.heroes.serializers import HeroSerializer

from .models import PlayerProgress


class PlayerProgressSerializer(serializers.ModelSerializer):
    department_detail = DepartmentSerializer(source="department", read_only=True)
    current_level_detail = LevelSerializer(source="current_level", read_only=True)

    class Meta:
        model = PlayerProgress
        fields = (
            "id", "department", "department_detail", "current_level", "current_level_detail",
            "stars", "total_score", "is_completed", "completed_at",
        )
        read_only_fields = fields


class CompleteLevelSerializer(serializers.Serializer):
    """Payload envoye a la fin d'un chapitre du mode Aventure."""

    level_id = serializers.UUIDField()
    score_percent = serializers.IntegerField(min_value=0, max_value=100)


class CompleteLevelResultSerializer(serializers.Serializer):
    progress = PlayerProgressSerializer()
    level_passed = serializers.BooleanField()
    xp_awarded = serializers.IntegerField()
    coin_awarded = serializers.IntegerField()
    hero_unlocked = HeroSerializer(allow_null=True)
