"""Vues DRF de l'app 'competition'."""
from rest_framework import viewsets

from .models import Event, Leaderboard, Season
from .serializers import EventSerializer, LeaderboardSerializer, SeasonSerializer


class SeasonViewSet(viewsets.ReadOnlyModelViewSet):
    """Saisons competitives (3 mois), passees et courante."""

    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    filterset_fields = ["is_active"]


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """Evenements ponctuels, rattaches ou non a une saison."""

    queryset = Event.objects.select_related("season").all()
    serializer_class = EventSerializer
    filterset_fields = ["season", "is_active"]


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Classements calcules periodiquement par Celery beat. Filtrer via
    ?scope=national|department|friends&period=weekly|monthly|yearly|season|all_time
    et eventuellement &department=<id>&season=<id>.
    """

    serializer_class = LeaderboardSerializer
    filterset_fields = ["scope", "period", "department", "season"]
    queryset = Leaderboard.objects.select_related("profile__user", "department", "season").order_by(
        "scope", "period", "rank"
    )
