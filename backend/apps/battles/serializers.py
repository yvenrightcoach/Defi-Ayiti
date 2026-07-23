"""Serializers DRF de l'app 'battles'."""
from rest_framework import serializers

from apps.accounts.serializers import UserProfileSerializer

from .models import BattleRoom, Match, MatchParticipant


class MatchParticipantSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = MatchParticipant
        fields = ("id", "profile", "score", "correct_answers", "rank", "joined_at")
        read_only_fields = fields


class MatchSerializer(serializers.ModelSerializer):
    participants = MatchParticipantSerializer(many=True, read_only=True)
    questions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Match
        fields = (
            "id", "room", "round_number", "questions", "question_count", "time_limit_seconds",
            "status", "winner", "started_at", "ended_at", "participants",
        )
        read_only_fields = ("id", "status", "winner", "started_at", "ended_at", "participants", "questions")


class CreateMatchSerializer(serializers.Serializer):
    """Cree un match dans une salle : questions tirees d'une categorie/departement."""

    category = serializers.UUIDField(required=False)
    department = serializers.UUIDField(required=False)
    question_count = serializers.IntegerField(default=10, min_value=1, max_value=30)
    time_limit_seconds = serializers.IntegerField(default=30, min_value=5, max_value=120)


class SubmitScoreSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=0)
    correct_answers = serializers.IntegerField(min_value=0)


class BattleRoomSerializer(serializers.ModelSerializer):
    host = UserProfileSerializer(read_only=True)
    participants = UserProfileSerializer(many=True, read_only=True)
    matches = MatchSerializer(many=True, read_only=True)

    class Meta:
        model = BattleRoom
        fields = (
            "id", "room_code", "room_type", "host", "participants", "max_players", "status",
            "rematch_of", "started_at", "finished_at", "matches",
        )
        read_only_fields = (
            "id", "room_code", "host", "participants", "status", "started_at", "finished_at", "matches",
        )


class CreateBattleRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = BattleRoom
        fields = ("room_type", "max_players")


class JoinRoomSerializer(serializers.Serializer):
    room_code = serializers.CharField(max_length=8)
