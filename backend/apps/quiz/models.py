"""Categories thematiques, questions et reponses du quiz."""
from django.db import models

from apps.core.models import BaseModel


class Category(BaseModel):
    """Grande thematique du quiz : Histoire, Geographie, Heros, Constitution, Civisme, Culture."""

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    icon = models.URLField(blank=True)
    color = models.CharField(max_length=7, default="#0057B8", help_text="Couleur hexadecimale")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Categorie"
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class Difficulty(models.TextChoices):
    EASY = "easy", "Facile"
    MEDIUM = "medium", "Moyen"
    HARD = "hard", "Difficile"


class QuestionType(models.TextChoices):
    MULTIPLE_CHOICE = "multiple_choice", "Choix multiple"
    TRUE_FALSE = "true_false", "Vrai/Faux"
    IMAGE = "image", "Question image"
    TIMELINE = "timeline", "Chronologie"
    MATCHING = "matching", "Association"
    MAP = "map", "Carte interactive"


class Question(BaseModel):
    """Une question de quiz, rattachee a une categorie et eventuellement a un chapitre d'aventure."""

    category = models.ForeignKey(Category, related_name="questions", on_delete=models.PROTECT)
    department = models.ForeignKey(
        "geography.Department", null=True, blank=True, related_name="questions", on_delete=models.SET_NULL
    )
    level = models.ForeignKey(
        "geography.Level", null=True, blank=True, related_name="questions", on_delete=models.SET_NULL
    )

    question_type = models.CharField(max_length=20, choices=QuestionType.choices, default=QuestionType.MULTIPLE_CHOICE)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.EASY)

    text = models.TextField()
    image = models.URLField(blank=True)
    explanation = models.TextField(blank=True, help_text="Affichee apres reponse, bonne ou mauvaise")
    xp_reward = models.PositiveIntegerField(default=10)
    is_boss_question = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "difficulty"]
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self) -> str:
        return self.text[:60]


class Answer(BaseModel):
    """Une reponse possible a une Question (une ou plusieurs peuvent etre correctes selon le type)."""

    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    text = models.CharField(max_length=255, blank=True)
    image = models.URLField(blank=True)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0, help_text="Ordre d'affichage / position correcte (chronologie, association)")

    class Meta:
        ordering = ["question", "order"]
        verbose_name = "Reponse"
        verbose_name_plural = "Reponses"

    def __str__(self) -> str:
        return f"{self.text[:40]} ({'correcte' if self.is_correct else 'incorrecte'})"
