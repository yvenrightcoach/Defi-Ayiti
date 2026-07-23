"""Vues DRF de l'app 'quiz'."""
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import UserProfile
from apps.rewards.models import PlayerMission

from .models import Category, Question
from .serializers import (
    AnswerResultSerializer,
    CategorySerializer,
    QuestionSerializer,
    SubmitAnswerSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Categories thematiques du quiz (Histoire, Geographie, Heros, Constitution, Civisme, Culture)."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Questions de quiz. La bonne reponse et l'explication ne sont jamais
    exposees ici : voir l'action 'submit' pour la correction.
    """

    serializer_class = QuestionSerializer
    filterset_fields = ["category", "department", "level", "difficulty", "question_type"]
    queryset = Question.objects.filter(is_active=True).select_related("category").prefetch_related("answers")

    @extend_schema(request=SubmitAnswerSerializer, responses=AnswerResultSerializer)
    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Soumet une reponse, la corrige et attribue l'XP + progression de mission."""
        question = self.get_object()
        payload = SubmitAnswerSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        submitted_ids = {str(a) for a in payload.validated_data["answer_ids"]}

        correct_answers = list(question.answers.filter(is_correct=True).values_list("id", flat=True))
        correct_ids = {str(a) for a in correct_answers}
        is_correct = submitted_ids == correct_ids

        xp_awarded = 0
        if is_correct:
            xp_awarded = question.xp_reward
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.add_xp(xp_awarded)
            self._progress_daily_missions(profile)

        result = AnswerResultSerializer(
            {
                "is_correct": is_correct,
                "correct_answer_ids": correct_answers,
                "explanation": question.explanation,
                "xp_awarded": xp_awarded,
            }
        )
        return Response(result.data)

    @staticmethod
    def _progress_daily_missions(profile: UserProfile) -> None:
        """Fait avancer les quetes 'repondre a des questions' du jour."""
        today = timezone.localdate()
        missions = PlayerMission.objects.filter(
            profile=profile,
            assigned_date=today,
            is_completed=False,
            mission__mission_type="answer_questions",
        ).select_related("mission")
        for player_mission in missions:
            player_mission.progress += 1
            if player_mission.progress >= player_mission.mission.target_value:
                player_mission.is_completed = True
                player_mission.completed_at = timezone.now()
            player_mission.save(update_fields=["progress", "is_completed", "completed_at"])
