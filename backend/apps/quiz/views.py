"""Vues DRF de l'app 'quiz'."""
from django.db.models import Q
from django.db.models.functions import Random
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

    MAX_LEVEL_SESSION_QUESTIONS = 50
    MAX_GENERAL_SESSION_QUESTIONS = 30

    @action(detail=False, methods=["get"])
    def session(self, request):
        """
        Tire des questions aleatoires pour une session de jeu : l'ordre et la
        selection changent a chaque appel, pour plus de difficulte et de
        rejouabilite. Un chapitre d'aventure (parametre 'level') tire jusqu'a
        50 questions ; un quiz rapide ou une battle en tire jusqu'a 30.

        Avec un niveau precise, combine les questions propres a ce chapitre
        et les questions generales (sans niveau ni departement), pour offrir
        un vrai brassage meme sur les chapitres a faible effectif.
        """
        level_id = request.query_params.get("level")
        max_allowed = self.MAX_LEVEL_SESSION_QUESTIONS if level_id else self.MAX_GENERAL_SESSION_QUESTIONS
        try:
            limit = min(int(request.query_params.get("limit", max_allowed)), max_allowed)
        except ValueError:
            limit = max_allowed

        qs = self.get_queryset()
        if level_id:
            qs = qs.filter(Q(level_id=level_id) | Q(level__isnull=True, department__isnull=True))
        else:
            category_id = request.query_params.get("category")
            department_id = request.query_params.get("department")
            if category_id:
                qs = qs.filter(category_id=category_id)
            if department_id:
                qs = qs.filter(department_id=department_id)

        questions = list(qs.order_by(Random())[:limit])
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)

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
