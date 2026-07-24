"""Utilisateur d'authentification et profil de jeu (XP, monnaies, ligue, collection)."""
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import BaseModel


class User(AbstractUser):
    """
    Utilisateur de la plateforme.

    Supporte l'authentification par email/mot de passe, Google, Facebook
    (via django-allauth) ainsi qu'un mode invite (is_guest=True).
    Les donnees de jeu (XP, monnaies, ligue...) vivent dans UserProfile.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    is_guest = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self) -> str:
        return self.username


class League(models.TextChoices):
    BRONZE = "bronze", "Bronze"
    SILVER = "silver", "Argent"
    GOLD = "gold", "Or"
    PLATINUM = "platinum", "Platine"
    DIAMOND = "diamond", "Diamant"
    MASTER = "master", "Maitre"
    CHAMPION = "champion", "Champion National"


class UserProfile(BaseModel):
    """Profil de jeu du joueur : progression, monnaies, competition, apparence."""

    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    avatar_url = models.URLField(blank=True)
    active_frame = models.ForeignKey(
        "rewards.Reward", null=True, blank=True, related_name="+", on_delete=models.SET_NULL
    )
    department = models.ForeignKey(
        "geography.Department", null=True, blank=True, related_name="players", on_delete=models.SET_NULL
    )

    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)
    trophies = models.PositiveIntegerField(default=0)
    coins = models.PositiveIntegerField(default=100)
    diamonds = models.PositiveIntegerField(default=0)

    league = models.CharField(max_length=20, choices=League.choices, default=League.BRONZE)
    win_streak = models.PositiveIntegerField(default=0)
    best_win_streak = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Profil joueur"
        verbose_name_plural = "Profils joueurs"

    def __str__(self) -> str:
        return f"Profil de {self.user.username}"

    def add_xp(self, amount: int) -> None:
        """Ajoute de l'XP et fait monter de niveau si le seuil (100 XP/niveau) est atteint."""
        self.xp += amount
        xp_per_level = 100
        self.level = max(1, self.xp // xp_per_level + 1)
        self.save(update_fields=["xp", "level"])
