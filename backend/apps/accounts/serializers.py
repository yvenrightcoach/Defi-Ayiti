"""Serializers DRF de l'app 'accounts'."""
from allauth.account.utils import user_pk_to_url_str
from dj_rest_auth.serializers import PasswordResetSerializer
from django.conf import settings
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


class ConvertDiamondsSerializer(serializers.Serializer):
    """Payload pour convertir des diamants (monnaie premium) en pieces."""

    diamonds = serializers.IntegerField(min_value=1)


class ConvertDiamondsResultSerializer(serializers.Serializer):
    coins = serializers.IntegerField()
    diamonds = serializers.IntegerField()


def _frontend_reset_url(_request, user, temp_key) -> str:
    """
    Remplace dj-rest-auth/allauth.forms.default_url_generator, qui pointe par
    defaut vers l'URL Django nommee 'password_reset_confirm' -- absente ici
    (seules allauth.socialaccount.urls sont montees, pas allauth.account.urls)
    -- par une page du frontend (SPA) qui appelle /auth/password/reset/confirm/.
    """
    uid = user_pk_to_url_str(user)
    return f"{settings.FRONTEND_URL}/reinitialiser-mot-de-passe?uid={uid}&token={temp_key}"


class CustomPasswordResetSerializer(PasswordResetSerializer):
    """Envoie un email de reinitialisation dont le lien pointe vers le frontend."""

    def get_email_options(self):
        return {"url_generator": _frontend_reset_url}
