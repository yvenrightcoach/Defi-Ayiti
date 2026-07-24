"""Achats reels (argent) de packs de diamants -- Stripe pour l'instant, PayPal ensuite."""
from django.db import models

from apps.core.models import BaseModel


class DiamondPack(BaseModel):
    """Pack de diamants achetable avec de l'argent reel."""

    name = models.CharField(max_length=80)
    diamonds_amount = models.PositiveIntegerField()
    price_usd_cents = models.PositiveIntegerField(help_text="Prix en cents USD (ex: 299 pour 2,99 $)")
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Pack de diamants"
        verbose_name_plural = "Packs de diamants"

    def __str__(self) -> str:
        return f"{self.name} ({self.diamonds_amount} diamants)"


class PaymentProvider(models.TextChoices):
    STRIPE = "stripe", "Stripe"
    PAYPAL = "paypal", "PayPal"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "En attente"
    PAID = "paid", "Paye"
    FAILED = "failed", "Echoue"
    CANCELLED = "cancelled", "Annule"


class DiamondPurchase(BaseModel):
    """
    Une transaction d'achat d'un pack de diamants. Creee en 'pending' des la
    creation de la session de paiement ; ne passe a 'paid' (et ne credite
    les diamants) que suite a la confirmation serveur-a-serveur du
    fournisseur (webhook), jamais sur la seule foi du retour navigateur du
    joueur.
    """

    profile = models.ForeignKey("accounts.UserProfile", related_name="diamond_purchases", on_delete=models.CASCADE)
    pack = models.ForeignKey(DiamondPack, related_name="purchases", on_delete=models.PROTECT)
    provider = models.CharField(max_length=20, choices=PaymentProvider.choices)
    provider_reference = models.CharField(
        max_length=255, unique=True, help_text="ID de session/commande cote fournisseur"
    )
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    diamonds_credited = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Achat de diamants"
        verbose_name_plural = "Achats de diamants"

    def __str__(self) -> str:
        return f"{self.profile} - {self.pack.name} ({self.status})"
