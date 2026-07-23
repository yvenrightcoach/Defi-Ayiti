"""Serializers DRF de l'app 'competition'."""
from rest_framework import serializers

from apps.accounts.serializers import UserProfileSerializer

from .models import Event, Leaderboard, Season


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = (
            "id", "name", "theme", "description", "banner_image",
            "start_date", "end_date", "is_active",
        )


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "id", "season", "name", "description", "banner_image",
            "start_at", "end_at", "reward", "is_active",
        )


class LeaderboardSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = Leaderboard
        fields = (
            "id", "scope", "period", "department", "season", "profile",
            "score", "rank", "period_start", "period_end", "generated_at",
        )
        read_only_fields = fields
