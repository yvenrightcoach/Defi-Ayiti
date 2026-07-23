"""Battles : duels 1v1, battles entre amis et tournois (8/16/32 joueurs)."""
from django.db import models

from apps.core.models import BaseModel


class RoomType(models.TextChoices):
    DUEL = "duel", "Duel 1v1"
    FRIEND = "friend", "Battle entre amis"
    TOURNAMENT = "tournament", "Tournoi"


class RoomStatus(models.TextChoices):
    WAITING = "waiting", "En attente"
    IN_PROGRESS = "in_progress", "En cours"
    FINISHED = "finished", "Termine"
    CANCELLED = "cancelled", "Annule"


class BattleRoom(BaseModel):
    """
    Salle de jeu : matchmaking d'un duel, lobby d'invitation entre amis
    (room_code prive) ou bracket de tournoi (8/16/32 joueurs).
    """

    room_code = models.CharField(max_length=8, unique=True, help_text="Code d'invitation (battle entre amis)")
    room_type = models.CharField(max_length=12, choices=RoomType.choices, default=RoomType.DUEL)
    host = models.ForeignKey("accounts.UserProfile", related_name="hosted_rooms", on_delete=models.CASCADE)
    participants = models.ManyToManyField(
        "accounts.UserProfile", related_name="joined_rooms", blank=True,
        help_text="Joueurs ayant rejoint la salle (hote inclus)",
    )
    max_players = models.PositiveSmallIntegerField(default=2, help_text="2 (duel/amis) ou 8/16/32 (tournoi)")
    status = models.CharField(max_length=12, choices=RoomStatus.choices, default=RoomStatus.WAITING)
    rematch_of = models.ForeignKey(
        "self", null=True, blank=True, related_name="rematches", on_delete=models.SET_NULL
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Salle de battle"
        verbose_name_plural = "Salles de battle"

    def __str__(self) -> str:
        return f"{self.get_room_type_display()} - {self.room_code}"


class MatchStatus(models.TextChoices):
    PENDING = "pending", "En attente"
    ONGOING = "ongoing", "En cours"
    FINISHED = "finished", "Termine"
    CANCELLED = "cancelled", "Annule"


class Match(BaseModel):
    """
    Une partie jouee (round d'un tournoi, ou partie unique pour un duel/battle
    entre amis) : memes questions pour tous les participants, temps limite.
    """

    room = models.ForeignKey(BattleRoom, related_name="matches", on_delete=models.CASCADE)
    round_number = models.PositiveSmallIntegerField(default=1, help_text="1 pour un duel ou une battle entre amis")
    questions = models.ManyToManyField("quiz.Question", related_name="matches", blank=True)
    question_count = models.PositiveSmallIntegerField(default=10)
    time_limit_seconds = models.PositiveSmallIntegerField(default=30, help_text="Par question")
    status = models.CharField(max_length=12, choices=MatchStatus.choices, default=MatchStatus.PENDING)
    winner = models.ForeignKey(
        "accounts.UserProfile", null=True, blank=True, related_name="matches_won", on_delete=models.SET_NULL
    )
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Match"
        verbose_name_plural = "Matchs"

    def __str__(self) -> str:
        return f"Match {self.id} (round {self.round_number}) - {self.room.room_code}"


class MatchParticipant(BaseModel):
    """Score d'un joueur dans un Match donne (table de jointure Match <-> UserProfile)."""

    match = models.ForeignKey(Match, related_name="participants", on_delete=models.CASCADE)
    profile = models.ForeignKey(
        "accounts.UserProfile", related_name="match_participations", on_delete=models.CASCADE
    )
    score = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveSmallIntegerField(default=0)
    rank = models.PositiveSmallIntegerField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("match", "profile")
        ordering = ["rank"]
        verbose_name = "Participant au match"
        verbose_name_plural = "Participants aux matchs"

    def __str__(self) -> str:
        return f"{self.profile} - {self.score} pts"
