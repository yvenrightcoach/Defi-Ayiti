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


LEVEL_XP_BASE = 100
LEVEL_XP_STEP = 50


def xp_required_for_level(level: int) -> int:
    """XP total cumule pour atteindre `level`. Chaque niveau exige LEVEL_XP_STEP
    de plus que le precedent (100, 150, 200, 250...), donc grimper de niveau
    devient volontairement plus long a mesure que le joueur progresse."""
    if level <= 1:
        return 0
    n = level - 1
    return LEVEL_XP_BASE * n + (LEVEL_XP_STEP * n * (n - 1)) // 2


def level_for_xp(xp: int) -> int:
    level = 1
    while xp >= xp_required_for_level(level + 1):
        level += 1
    return level


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
    avatar_hero = models.ForeignKey(
        "heroes.Hero",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
        help_text="Heros debloque choisi comme photo de profil (remplace avatar_url a l'affichage)",
    )
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
    last_seen = models.DateTimeField(null=True, blank=True, help_text="Derniere requete authentifiee (presence en ligne)")

    class Meta:
        verbose_name = "Profil joueur"
        verbose_name_plural = "Profils joueurs"

    def __str__(self) -> str:
        return f"Profil de {self.user.username}"

    @property
    def xp_into_level(self) -> int:
        return self.xp - xp_required_for_level(self.level)

    @property
    def xp_for_next_level(self) -> int:
        return xp_required_for_level(self.level + 1) - xp_required_for_level(self.level)

    def add_xp(self, amount: int) -> None:
        """Ajoute de l'XP et fait monter de niveau selon le seuil croissant (voir level_for_xp)."""
        self.xp += amount
        self.level = level_for_xp(self.xp)
        self.save(update_fields=["xp", "level"])
        if amount > 0:
            # Import tardif : evite une dependance circulaire au chargement des apps.
            from apps.competition.models import ScoreEvent

            ScoreEvent.objects.create(profile=self, amount=amount)
