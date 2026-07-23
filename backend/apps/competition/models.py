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
    DEPARTMENT = "department", "Departement"
    FRIENDS = "friends", "Amis"


class LeaderboardPeriod(models.TextChoices):
    WEEKLY = "weekly", "Hebdomadaire"
    MONTHLY = "monthly", "Mensuel"
    YEARLY = "yearly", "Annuel"
    SEASON = "season", "Saison"
    ALL_TIME = "all_time", "Historique"


class Leaderboard(BaseModel):
    """
    Ligne de classement : le rang d'un profil pour une portee/periode donnee.
    Recalcule periodiquement par Celery beat (voir config/celery.py).
    """

    scope = models.CharField(max_length=12, choices=LeaderboardScope.choices, default=LeaderboardScope.NATIONAL)
    period = models.CharField(max_length=10, choices=LeaderboardPeriod.choices, default=LeaderboardPeriod.WEEKLY)
    department = models.ForeignKey(
        "geography.Department", null=True, blank=True, related_name="leaderboards", on_delete=models.CASCADE
    )
    season = models.ForeignKey(Season, null=True, blank=True, related_name="leaderboards", on_delete=models.CASCADE)
    profile = models.ForeignKey("accounts.UserProfile", related_name="leaderboard_entries", on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField()
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("scope", "period", "department", "season", "profile", "period_start")
        ordering = ["scope", "period", "rank"]
        verbose_name = "Classement"
        verbose_name_plural = "Classements"

    def __str__(self) -> str:
        return f"#{self.rank} {self.profile} ({self.get_scope_display()}/{self.get_period_display()})"
