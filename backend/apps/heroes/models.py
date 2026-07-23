"""Collection de heros historiques et cartes de collection debloquees par les joueurs."""
from django.db import models

from apps.core.models import BaseModel


class Hero(BaseModel):
    """Un heros historique haitien, avec sa biographie et sa condition de deblocage."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    image = models.URLField(blank=True)
    card_image = models.URLField(blank=True, help_text="Illustration de la carte de collection")
    biography = models.TextField()
    quote = models.CharField(max_length=280, blank=True)
    department = models.ForeignKey(
        "geography.Department", null=True, blank=True, related_name="heroes", on_delete=models.SET_NULL
    )
    unlock_level = models.PositiveIntegerField(
        default=1, help_text="Niveau de joueur minimum requis (independamment d'un chapitre precis)"
    )
    rarity = models.CharField(
        max_length=20,
        choices=[
            ("common", "Commun"),
            ("rare", "Rare"),
            ("epic", "Epique"),
            ("legendary", "Legendaire"),
        ],
        default="common",
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Heros"
        verbose_name_plural = "Heros"

    def __str__(self) -> str:
        return self.name


class HeroCard(BaseModel):
    """
    Carte de collection : instance d'un Hero debloque par un joueur.
    Materialise la "collection de heros" du profil (avec animation de deblocage
    declenchee cote frontend a la creation de cet enregistrement).
    """

    profile = models.ForeignKey("accounts.UserProfile", related_name="hero_cards", on_delete=models.CASCADE)
    hero = models.ForeignKey(Hero, related_name="cards", on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    unlocked_via_level = models.ForeignKey(
        "geography.Level", null=True, blank=True, related_name="+", on_delete=models.SET_NULL
    )

    class Meta:
        unique_together = ("profile", "hero")
        ordering = ["-unlocked_at"]
        verbose_name = "Carte de heros"
        verbose_name_plural = "Cartes de heros"

    def __str__(self) -> str:
        return f"{self.profile} - {self.hero.name}"
