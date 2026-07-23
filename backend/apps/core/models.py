"""Modeles abstraits partages par toutes les apps de jeu."""
import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """Modele abstrait ajoutant les champs de creation/mise a jour."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Modele abstrait avec une cle primaire UUID (non devinable, safe a exposer via l'API)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel):
    """Combine UUIDModel et TimeStampedModel : base standard des modeles de jeu."""

    class Meta:
        abstract = True
