"""Notifications in-app (demandes d'ami, defis, achievements, saisons, systeme)."""
from django.db import models

from apps.core.models import BaseModel


class NotificationType(models.TextChoices):
    FRIEND_REQUEST = "friend_request", "Demande d'ami"
    CHALLENGE = "challenge", "Defi"
    ACHIEVEMENT = "achievement", "Achievement debloque"
    SEASON = "season", "Saison"
    REWARD = "reward", "Recompense"
    SYSTEM = "system", "Systeme"


class Notification(BaseModel):
    """Notification envoyee a un profil, avec une action optionnelle (deep-link frontend)."""

    profile = models.ForeignKey("accounts.UserProfile", related_name="notifications", on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    title = models.CharField(max_length=140)
    message = models.TextField(blank=True)
    action_url = models.CharField(max_length=255, blank=True, help_text="Route frontend a ouvrir, ex: /amis")
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self) -> str:
        return f"{self.profile} - {self.title}"
