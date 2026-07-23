"""Recompenses generiques, badges, quetes quotidiennes et boutique."""
from django.db import models

from apps.core.models import BaseModel


class RewardType(models.TextChoices):
    COINS = "coins", "Pieces"
    DIAMONDS = "diamonds", "Diamants"
    BADGE = "badge", "Badge"
    AVATAR = "avatar", "Avatar"
    FRAME = "frame", "Cadre de profil"
    HERO = "hero", "Heros"
    CHEST_BRONZE = "chest_bronze", "Coffre bronze"
    CHEST_SILVER = "chest_silver", "Coffre argent"
    CHEST_GOLD = "chest_gold", "Coffre or"


class Reward(BaseModel):
    """
    Recompense generique distribuee par une Mission, un Achievement, un Event
    ou obtenue via un coffre. Le contenu effectif depend de reward_type.
    """

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    reward_type = models.CharField(max_length=20, choices=RewardType.choices)
    image = models.URLField(blank=True)
    coins_amount = models.PositiveIntegerField(default=0)
    diamonds_amount = models.PositiveIntegerField(default=0)
    xp_amount = models.PositiveIntegerField(default=0)
    grants_hero = models.ForeignKey(
        "heroes.Hero", null=True, blank=True, related_name="granted_by_rewards", on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = "Recompense"
        verbose_name_plural = "Recompenses"

    def __str__(self) -> str:
        return self.name


class Achievement(BaseModel):
    """Definition d'un badge/trophee obtenu en atteignant un critere de jeu."""

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    icon = models.URLField(blank=True)
    criteria_type = models.CharField(
        max_length=30,
        choices=[
            ("questions_answered", "Questions repondues"),
            ("matches_won", "Matchs gagnes"),
            ("win_streak", "Serie de victoires"),
            ("departments_completed", "Departements termines"),
            ("heroes_collected", "Heros collectionnes"),
        ],
    )
    criteria_value = models.PositiveIntegerField()
    reward = models.ForeignKey(Reward, null=True, blank=True, related_name="achievements", on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"

    def __str__(self) -> str:
        return self.name


class PlayerAchievement(BaseModel):
    """Progression/deblocage d'un Achievement par un joueur (table de jointure)."""

    profile = models.ForeignKey("accounts.UserProfile", related_name="achievements", on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, related_name="unlocked_by", on_delete=models.CASCADE)
    progress = models.PositiveIntegerField(default=0)
    unlocked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("profile", "achievement")
        verbose_name = "Achievement du joueur"
        verbose_name_plural = "Achievements des joueurs"

    def __str__(self) -> str:
        return f"{self.profile} - {self.achievement.name}"


class MissionType(models.TextChoices):
    ANSWER_QUESTIONS = "answer_questions", "Repondre a des questions"
    WIN_MATCHES = "win_matches", "Gagner des matchs"
    CORRECT_STREAK = "correct_streak", "Serie de bonnes reponses"
    PLAY_DEPARTMENT = "play_department", "Jouer dans un departement"


class Mission(BaseModel):
    """Definition d'une quete (quotidienne par defaut)."""

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    mission_type = models.CharField(max_length=20, choices=MissionType.choices)
    target_value = models.PositiveIntegerField(help_text="Ex: 20 pour 'Repondre a 20 questions'")
    xp_reward = models.PositiveIntegerField(default=20)
    coin_reward = models.PositiveIntegerField(default=10)
    is_daily = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Mission"
        verbose_name_plural = "Missions"

    def __str__(self) -> str:
        return self.name


class PlayerMission(BaseModel):
    """
    Assignation d'une Mission a un joueur pour une date donnee, avec sa
    progression. Reinitialisee chaque jour par la tache Celery
    reset_daily_missions (voir config/celery.py).
    """

    profile = models.ForeignKey("accounts.UserProfile", related_name="missions", on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, related_name="assignments", on_delete=models.CASCADE)
    assigned_date = models.DateField(auto_now_add=True)
    progress = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    reward_claimed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("profile", "mission", "assigned_date")
        verbose_name = "Mission du joueur"
        verbose_name_plural = "Missions des joueurs"

    def __str__(self) -> str:
        return f"{self.profile} - {self.mission.name} ({self.assigned_date})"


class ShopItemType(models.TextChoices):
    AVATAR = "avatar", "Avatar"
    FRAME = "frame", "Cadre de profil"
    BOOSTER = "booster", "Booster"


class ShopItem(BaseModel):
    """Article achetable dans la boutique avec des pieces ou des diamants."""

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=10, choices=ShopItemType.choices)
    image = models.URLField(blank=True)
    price_coins = models.PositiveIntegerField(default=0)
    price_diamonds = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Article boutique"
        verbose_name_plural = "Articles boutique"

    def __str__(self) -> str:
        return self.name


class Purchase(BaseModel):
    """Historique d'achat d'un ShopItem par un joueur."""

    profile = models.ForeignKey("accounts.UserProfile", related_name="purchases", on_delete=models.CASCADE)
    shop_item = models.ForeignKey(ShopItem, related_name="purchases", on_delete=models.PROTECT)
    price_paid_coins = models.PositiveIntegerField(default=0)
    price_paid_diamonds = models.PositiveIntegerField(default=0)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-purchased_at"]
        verbose_name = "Achat"
        verbose_name_plural = "Achats"

    def __str__(self) -> str:
        return f"{self.profile} - {self.shop_item.name}"
