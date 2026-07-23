"""Progression du joueur dans le mode Aventure (departements et chapitres)."""
from django.db import models

from apps.core.models import BaseModel


class PlayerProgress(BaseModel):
    """
    Avancement d'un joueur dans un departement : chapitre courant, etoiles et
    score cumules. Une ligne par (profile, department).
    """

    profile = models.ForeignKey("accounts.UserProfile", related_name="progress_entries", on_delete=models.CASCADE)
    department = models.ForeignKey("geography.Department", related_name="progress_entries", on_delete=models.CASCADE)
    current_level = models.ForeignKey(
        "geography.Level", null=True, blank=True, related_name="+", on_delete=models.SET_NULL
    )
    stars = models.PositiveSmallIntegerField(default=0)
    total_score = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False, help_text="Tous les chapitres + boss final termines")
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("profile", "department")
        verbose_name = "Progression"
        verbose_name_plural = "Progressions"

    def __str__(self) -> str:
        return f"{self.profile} - {self.department.name}"
