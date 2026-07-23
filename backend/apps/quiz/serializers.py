"""Serializers DRF de l'app 'quiz'."""
from rest_framework import serializers

from .models import Answer, Category, Question


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "icon", "color", "order")


class PublicAnswerSerializer(serializers.ModelSerializer):
    """Reponse telle qu'exposee au joueur AVANT de repondre : jamais is_correct."""

    class Meta:
        model = Answer
        fields = ("id", "text", "image", "order")


class QuestionSerializer(serializers.ModelSerializer):
    """
    Question telle qu'exposee au joueur avant reponse : ni 'explanation' ni
    'is_correct' des reponses ne sont inclus (evite de reveler la solution).
    """

    answers = PublicAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = (
            "id", "category", "department", "level", "question_type", "difficulty",
            "text", "image", "xp_reward", "is_boss_question", "answers",
        )


class SubmitAnswerSerializer(serializers.Serializer):
    """Payload de soumission de reponse : un ou plusieurs ids de reponse selectionnes."""

    answer_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)


class AnswerResultSerializer(serializers.Serializer):
    """Resultat renvoye apres soumission : correction et pedagogie."""

    is_correct = serializers.BooleanField()
    correct_answer_ids = serializers.ListField(child=serializers.UUIDField())
    explanation = serializers.CharField(allow_blank=True)
    xp_awarded = serializers.IntegerField()
