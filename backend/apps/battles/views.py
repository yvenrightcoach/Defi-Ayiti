"""Vues DRF de l'app 'battles'."""
import random
import string

from django.db.models import Q
from django.db.models.functions import Random
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.accounts.models import UserProfile
from apps.quiz.models import Question

from .models import BattleRoom, Match, MatchParticipant, RoomStatus
from .serializers import (
    BattleRoomSerializer,
    CreateBattleRoomSerializer,
    CreateMatchSerializer,
    JoinRoomSerializer,
    MatchSerializer,
    SubmitScoreSerializer,
)


def _generate_room_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = "".join(random.choices(alphabet, k=6))
        if not BattleRoom.objects.filter(room_code=code).exists():
            return code


class BattleRoomViewSet(viewsets.ModelViewSet):
    """Salles de battle : duel, entre amis (code prive) ou tournoi."""

    http_method_names = ["get", "post", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateBattleRoomSerializer
        return BattleRoomSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return BattleRoom.objects.none()
        profile = UserProfile.objects.filter(user=self.request.user).first()
        return (
            BattleRoom.objects.filter(Q(host=profile) | Q(participants=profile))
            .distinct()
            .select_related("host__user")
            .prefetch_related("matches__participants__profile__user")
        )

    def perform_create(self, serializer):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        room = serializer.save(host=profile, room_code=_generate_room_code())
        room.participants.add(profile)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        room = serializer.instance
        return Response(BattleRoomSerializer(room).data, status=201)

    @action(detail=False, methods=["post"])
    def join(self, request):
        """Rejoint une salle prive via son code (battle entre amis)."""
        payload = JoinRoomSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        try:
            room = BattleRoom.objects.get(room_code=payload.validated_data["room_code"].upper())
        except BattleRoom.DoesNotExist as exc:
            raise NotFound("Code de salle invalide.") from exc
        if room.status != RoomStatus.WAITING:
            raise ValidationError("Cette salle n'accepte plus de joueurs.")
        if room.participants.count() >= room.max_players:
            raise ValidationError("Cette salle est complete.")

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        room.participants.add(profile)
        return Response(BattleRoomSerializer(room).data)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        """L'hote lance un match : tire question_count questions selon les filtres fournis."""
        room = self.get_object()
        profile = UserProfile.objects.filter(user=request.user).first()
        if room.host_id != profile.id:
            raise PermissionDenied("Seul l'hote peut lancer la partie.")

        payload = CreateMatchSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        data = payload.validated_data

        questions_qs = Question.objects.filter(is_active=True)
        if data.get("category"):
            questions_qs = questions_qs.filter(category_id=data["category"])
        if data.get("department"):
            questions_qs = questions_qs.filter(department_id=data["department"])

        question_count = data["question_count"]
        questions = list(questions_qs.order_by(Random())[:question_count])
        if not questions:
            raise ValidationError("Aucune question ne correspond aux criteres selectionnes.")

        match = Match.objects.create(
            room=room,
            round_number=room.matches.count() + 1,
            question_count=len(questions),
            time_limit_seconds=data["time_limit_seconds"],
            status="ongoing",
            started_at=timezone.now(),
        )
        match.questions.set(questions)
        for room_profile in room.participants.all():
            MatchParticipant.objects.get_or_create(match=match, profile=room_profile)

        room.status = RoomStatus.IN_PROGRESS
        room.started_at = room.started_at or timezone.now()
        room.save(update_fields=["status", "started_at"])

        return Response(MatchSerializer(match).data, status=201)


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """Parties jouees : consultation, soumission de score et cloture."""

    serializer_class = MatchSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Match.objects.none()
        profile = UserProfile.objects.filter(user=self.request.user).first()
        return (
            Match.objects.filter(Q(room__host=profile) | Q(room__participants=profile))
            .distinct()
            .select_related("room")
            .prefetch_related("participants__profile__user")
        )

    @extend_schema(request=SubmitScoreSerializer, responses=MatchSerializer)
    @action(detail=True, methods=["post"], url_path="submit-score")
    def submit_score(self, request, pk=None):
        """Enregistre/actualise le score du joueur connecte pour ce match."""
        match = self.get_object()
        payload = SubmitScoreSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        participant, _ = MatchParticipant.objects.update_or_create(
            match=match,
            profile=profile,
            defaults={
                "score": payload.validated_data["score"],
                "correct_answers": payload.validated_data["correct_answers"],
            },
        )
        return Response(MatchSerializer(match).data)

    @action(detail=True, methods=["post"])
    def finish(self, request, pk=None):
        """Cloture le match : classe les participants et recompense le gagnant."""
        match = self.get_object()
        profile = UserProfile.objects.filter(user=request.user).first()
        if match.room.host_id != profile.id:
            raise PermissionDenied("Seul l'hote peut cloturer la partie.")

        participants = list(match.participants.select_related("profile").order_by("-score"))
        for rank, participant in enumerate(participants, start=1):
            participant.rank = rank
            participant.save(update_fields=["rank"])

        match.status = "finished"
        match.ended_at = timezone.now()
        if participants:
            winner_participant = participants[0]
            match.winner = winner_participant.profile
            winner_profile = winner_participant.profile
            winner_profile.trophies += 20
            winner_profile.win_streak += 1
            winner_profile.best_win_streak = max(winner_profile.best_win_streak, winner_profile.win_streak)
            winner_profile.save(update_fields=["trophies", "win_streak", "best_win_streak"])
            for loser in participants[1:]:
                loser.profile.win_streak = 0
                loser.profile.save(update_fields=["win_streak"])
        match.save(update_fields=["status", "ended_at", "winner"])

        match.room.status = RoomStatus.FINISHED
        match.room.finished_at = timezone.now()
        match.room.save(update_fields=["status", "finished_at"])

        return Response(MatchSerializer(match).data)
