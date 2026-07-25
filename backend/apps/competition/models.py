"""Saisons (3 mois), evenements et classements (national / departement / amis)."""
from django.db import models

from apps.core.models import BaseModel


class Season(BaseModel):
    """Saison competitive d'environ 3 mois, avec theme et recompenses exclusives."""

    name = models.CharField(max_length=120, unique=True)
    theme = models.CharField(max_length=160, blank=True, help_text="Ex: Saison des heros de l'independance")
    description = models.TextField(blank=True)
    banner_image = models.URLField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Saison"
        verbose_name_plural = "Saisons"

    def __str__(self) -> str:
        return self.name


class Event(BaseModel):
    """Evenement ponctuel/limite dans le temps, rattache ou non a une Season."""

    season = models.ForeignKey(Season, null=True, blank=True, related_name="events", on_delete=models.SET_NULL)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    banner_image = models.URLField(blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    reward = models.ForeignKey(
        "rewards.Reward", null=True, blank=True, related_name="events", on_delete=models.SET_NULL
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-start_at"]
        verbose_name = "Evenement"
        verbose_name_plural = "Evenements"

    def __str__(self) -> str:
        return self.name


class LeaderboardScope(models.TextChoices):
    NATIONAL = "national", "National"
    FRIENDS = "friends", "Amis"


class LeaderboardPeriod(models.TextChoices):
    WEEKLY = "weekly", "Hebdomadaire"
    MONTHLY = "monthly", "Mensuel"
    YEARLY = "yearly", "Annuel"


class ScoreEvent(BaseModel):
    """
    Ligne d'historique horodatee a chaque gain d'XP (voir UserProfile.add_xp).
    Sert de base au calcul live des classements hebdo/mensuel/annuel : le
    score d'une periode est la somme des `amount` dont `created_at` tombe
    dans la fenetre de cette periode -- pas de tache planifiee requise.
    """

    profile = models.ForeignKey("accounts.UserProfile", related_name="score_events", on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["profile", "created_at"])]
        verbose_name = "Evenement de score"
        verbose_name_plural = "Evenements de score"

    def __str__(self) -> str:
        return f"+{self.amount} pour {self.profile} ({self.created_at:%Y-%m-%d})"


class PeriodWinner(BaseModel):
    """
    Vainqueur fige du classement national a la cloture d'une periode
    (semaine/mois/annee) -- calcule paresseusement au premier appel de
    l'API de classement suivant la cloture (voir competition/views.py),
    puisque le plan gratuit Render n'a pas de Celery beat.
    """

    scope = models.CharField(max_length=12, choices=LeaderboardScope.choices, default=LeaderboardScope.NATIONAL)
    period = models.CharField(max_length=10, choices=LeaderboardPeriod.choices)
    period_key = models.CharField(max_length=16, help_text="Ex: 2026-W30, 2026-07, 2026")
    profile = models.ForeignKey("accounts.UserProfile", related_name="period_wins", on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    coins_awarded = models.PositiveIntegerField(default=0)
    diamonds_awarded = models.PositiveIntegerField(default=0)
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("scope", "period", "period_key")
        ordering = ["-granted_at"]
        verbose_name = "Vainqueur de periode"
        verbose_name_plural = "Vainqueurs de periode"

    def __str__(self) -> str:
        return f"{self.period_key} ({self.get_period_display()}): {self.profile}"
