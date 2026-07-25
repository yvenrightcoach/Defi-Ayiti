"""Vues DRF de l'app 'competition'."""
from datetime import timedelta

from django.db.models import F, Sum
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserProfile
from apps.social.services import get_accepted_friend_ids

from .models import Event, LeaderboardPeriod, LeaderboardScope, PeriodWinner, ScoreEvent, Season
from .serializers import EventSerializer, LeaderboardResponseSerializer, SeasonSerializer

# Recompenses accordees au 1er du classement national a la cloture de
# chaque periode -- montants choisis pour rester incitatifs sans devaluer
# les autres sources de pieces/diamants du jeu (mise de pieces, missions...).
PERIOD_REWARDS = {
    LeaderboardPeriod.WEEKLY: {"coins": 200, "diamonds": 10},
    LeaderboardPeriod.MONTHLY: {"coins": 800, "diamonds": 40},
    LeaderboardPeriod.YEARLY: {"coins": 3000, "diamonds": 150},
}


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


def _week_bounds(now):
    monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    end = monday + timedelta(weeks=1)
    iso_year, iso_week, _ = monday.isocalendar()
    return monday, end, f"{iso_year}-W{iso_week:02d}"


def _month_bounds(now):
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = start.replace(year=start.year + 1, month=1) if start.month == 12 else start.replace(month=start.month + 1)
    return start, end, f"{start.year}-{start.month:02d}"


def _year_bounds(now):
    start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    end = start.replace(year=start.year + 1)
    return start, end, f"{start.year}"


_BOUNDS_FN = {
    LeaderboardPeriod.WEEKLY: _week_bounds,
    LeaderboardPeriod.MONTHLY: _month_bounds,
    LeaderboardPeriod.YEARLY: _year_bounds,
}


def _period_bounds(period, now):
    return _BOUNDS_FN[period](now)


def _previous_period_bounds(period, current_start):
    # Un instant juste avant le debut de la periode courante retombe
    # forcement dans la periode precedente -- evite de dupliquer la logique
    # de recul (mois/annee a longueur variable) pour chaque type de periode.
    return _period_bounds(period, current_start - timedelta(microseconds=1))


def _finalize_previous_period(period, current_start):
    """
    Cloture paresseusement la periode qui vient de se terminer : si elle n'a
    pas encore de vainqueur enregistre, calcule le 1er du classement national
    sur cette fenetre et lui accorde sa recompense. Appele a chaque requete
    de classement puisque le plan gratuit Render n'a pas de Celery beat.
    """
    prev_start, prev_end, prev_key = _previous_period_bounds(period, current_start)
    if PeriodWinner.objects.filter(scope=LeaderboardScope.NATIONAL, period=period, period_key=prev_key).exists():
        return

    top = (
        ScoreEvent.objects.filter(created_at__gte=prev_start, created_at__lt=prev_end)
        .values("profile")
        .annotate(total=Sum("amount"))
        .order_by("-total")
        .first()
    )
    if not top:
        return

    reward = PERIOD_REWARDS[period]
    _winner, created = PeriodWinner.objects.get_or_create(
        scope=LeaderboardScope.NATIONAL,
        period=period,
        period_key=prev_key,
        defaults={
            "profile_id": top["profile"],
            "score": top["total"],
            "coins_awarded": reward["coins"],
            "diamonds_awarded": reward["diamonds"],
        },
    )
    if created:
        UserProfile.objects.filter(pk=top["profile"]).update(
            coins=F("coins") + reward["coins"], diamonds=F("diamonds") + reward["diamonds"]
        )


class LeaderboardView(APIView):
    """
    Classement national (tous les joueurs actifs) ou entre amis, calcule en
    direct a partir de ScoreEvent -- aucune tache planifiee necessaire.
    ?scope=national|friends&period=weekly|monthly|yearly
    """

    def get(self, request):
        scope = request.query_params.get("scope", LeaderboardScope.NATIONAL)
        period = request.query_params.get("period", LeaderboardPeriod.WEEKLY)
        if scope not in LeaderboardScope.values:
            raise ValidationError({"scope": "Valeur invalide."})
        if period not in LeaderboardPeriod.values:
            raise ValidationError({"period": "Valeur invalide."})

        profile = UserProfile.objects.filter(user=request.user).first()
        now = timezone.now()
        start, end, period_key = _period_bounds(period, now)

        _finalize_previous_period(period, start)

        events = ScoreEvent.objects.filter(created_at__gte=start, created_at__lt=end)

        if scope == LeaderboardScope.FRIENDS:
            member_ids = set(get_accepted_friend_ids(profile))
            if profile is not None:
                member_ids.add(profile.id)
            profiles = list(UserProfile.objects.filter(id__in=member_ids).select_related("user", "department"))
            totals = {row["profile"]: row["total"] for row in events.filter(profile_id__in=member_ids).values("profile").annotate(total=Sum("amount"))}
            scored = {p.id: totals.get(p.id, 0) for p in profiles}
        else:
            totals = {row["profile"]: row["total"] for row in events.values("profile").annotate(total=Sum("amount"))}
            profiles = list(UserProfile.objects.filter(id__in=totals.keys()).select_related("user", "department"))
            scored = totals

        ranked = sorted(profiles, key=lambda p: scored.get(p.id, 0), reverse=True)
        entries = [{"rank": index + 1, "profile": p, "score": scored.get(p.id, 0)} for index, p in enumerate(ranked[:100])]
        my_rank = next((index + 1 for index, p in enumerate(ranked) if profile and p.id == profile.id), None)

        prev_winner = (
            PeriodWinner.objects.filter(scope=LeaderboardScope.NATIONAL, period=period)
            .exclude(period_key=period_key)
            .select_related("profile__user")
            .order_by("-granted_at")
            .first()
        )
        previous_winner = (
            {"username": prev_winner.profile.user.username, "score": prev_winner.score, "period_key": prev_winner.period_key}
            if prev_winner
            else None
        )

        data = {
            "scope": scope,
            "period": period,
            "period_start": start,
            "period_end": end,
            "entries": entries,
            "my_rank": my_rank,
            "reward": PERIOD_REWARDS[period],
            "previous_winner": previous_winner,
        }
        return Response(LeaderboardResponseSerializer(data).data)
