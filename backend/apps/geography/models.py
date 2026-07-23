"""Mode Aventure : les 10 departements d'Haiti et leurs chapitres (Level)."""
from django.db import models

from apps.core.models import BaseModel


class Department(BaseModel):
    """Une zone du mode Aventure, correspondant a un departement d'Haiti."""

    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    code = models.CharField(max_length=6, unique=True, help_text="Ex: OU, ND, NE, NO, ART, CTR, SUD, SE, GA, NIP")
    capital = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    map_image = models.URLField(blank=True, help_text="Image/illustration sur la carte interactive")
    icon = models.URLField(blank=True)
    boss_name = models.CharField(max_length=120, blank=True, help_text="Nom du boss final du departement")
    order = models.PositiveSmallIntegerField(default=0, help_text="Ordre d'apparition sur la carte")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Departement"
        verbose_name_plural = "Departements"

    def __str__(self) -> str:
        return self.name


class Level(BaseModel):
    """
    Un chapitre/niveau du mode Aventure au sein d'un departement.
    Terminer un chapitre peut debloquer un heros (unlocks_hero).
    """

    department = models.ForeignKey(Department, related_name="levels", on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=1)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    question_count = models.PositiveSmallIntegerField(default=10)
    required_score = models.PositiveSmallIntegerField(
        default=70, help_text="Pourcentage minimum de bonnes reponses pour valider le chapitre"
    )
    xp_reward = models.PositiveIntegerField(default=50)
    coin_reward = models.PositiveIntegerField(default=20)
    is_boss_level = models.BooleanField(default=False)
    unlocks_hero = models.ForeignKey(
        "heroes.Hero", null=True, blank=True, related_name="unlocked_by_levels", on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["department__order", "order"]
        unique_together = ("department", "order")
        verbose_name = "Chapitre"
        verbose_name_plural = "Chapitres"

    def __str__(self) -> str:
        return f"{self.department.name} - Chapitre {self.order} : {self.name}"
