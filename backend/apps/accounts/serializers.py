"""Serializers DRF de l'app 'accounts'."""
from rest_framework import serializers

from apps.geography.serializers import DepartmentSerializer

from .models import User, UserProfile


class UserBasicSerializer(serializers.ModelSerializer):
    """Identite publique minimale d'un utilisateur (utilisee en imbrique)."""

    class Meta:
        model = User
        fields = ("id", "username", "is_guest")
        read_only_fields = fields


class UserProfileSerializer(serializers.ModelSerializer):
    """Profil de jeu complet -- utilise pour /accounts/me/ et la lecture publique."""

    user = UserBasicSerializer(read_only=True)
    department_detail = DepartmentSerializer(source="department", read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "id", "user", "avatar_url", "active_frame", "department", "department_detail",
            "level", "xp", "points", "trophies", "coins", "diamonds",
            "league", "win_streak", "best_win_streak", "created_at",
        )
        read_only_fields = (
            "id", "user", "level", "xp", "points", "trophies", "coins", "diamonds",
            "league", "win_streak", "best_win_streak", "created_at", "department_detail",
        )


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Champs modifiables par le joueur lui-meme sur son propre profil."""

    class Meta:
        model = UserProfile
        fields = ("avatar_url", "active_frame", "department")


class GuestLoginResponseSerializer(serializers.Serializer):
    """Reponse de /accounts/guest/ : jetons JWT + identite minimale."""

    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserBasicSerializer()
