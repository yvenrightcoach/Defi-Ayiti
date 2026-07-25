"""Serializers DRF de l'app 'competition'."""
from rest_framework import serializers

from apps.accounts.serializers import UserProfileSerializer

from .models import Event, Season


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


class LeaderboardRowSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    profile = UserProfileSerializer()
    score = serializers.IntegerField()


class LeaderboardRewardSerializer(serializers.Serializer):
    coins = serializers.IntegerField()
    diamonds = serializers.IntegerField()


class PeriodWinnerSerializer(serializers.Serializer):
    username = serializers.CharField()
    score = serializers.IntegerField()
    period_key = serializers.CharField()


class LeaderboardResponseSerializer(serializers.Serializer):
    scope = serializers.CharField()
    period = serializers.CharField()
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    entries = LeaderboardRowSerializer(many=True)
    my_rank = serializers.IntegerField(allow_null=True)
    reward = LeaderboardRewardSerializer()
    previous_winner = PeriodWinnerSerializer(allow_null=True)
