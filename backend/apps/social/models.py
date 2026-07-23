"""Systeme d'amis : demandes, acceptation et defis."""
from django.db import models

from apps.core.models import BaseModel


class FriendStatus(models.TextChoices):
    PENDING = "pending", "En attente"
    ACCEPTED = "accepted", "Acceptee"
    DECLINED = "declined", "Refusee"


class Friend(BaseModel):
    """Relation d'amitie entre deux joueurs, initiee par 'requester'."""

    requester = models.ForeignKey(
        "accounts.UserProfile", related_name="friend_requests_sent", on_delete=models.CASCADE
    )
    addressee = models.ForeignKey(
        "accounts.UserProfile", related_name="friend_requests_received", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=FriendStatus.choices, default=FriendStatus.PENDING)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("requester", "addressee")
        verbose_name = "Amitie"
        verbose_name_plural = "Amities"

    def __str__(self) -> str:
        return f"{self.requester} -> {self.addressee} ({self.status})"
