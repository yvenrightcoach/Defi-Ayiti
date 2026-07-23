"""Vues DRF de l'app 'progress'."""
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from apps.accounts.models import UserProfile
from apps.geography.models import Level
from apps.heroes.models import HeroCard

from .models import PlayerProgress
from .serializers import (
    CompleteLevelResultSerializer,
    CompleteLevelSerializer,
    PlayerProgressSerializer,
)


class PlayerProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """Progression du joueur connecte dans le mode Aventure (par departement)."""

    serializer_class = PlayerProgressSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return PlayerProgress.objects.none()
        return PlayerProgress.objects.filter(profile__user=self.request.user).select_related(
            "department", "current_level"
        )

    @extend_schema(request=CompleteLevelSerializer, responses=CompleteLevelResultSerializer)
    @action(detail=False, methods=["post"], url_path="complete-level")
    def complete_level(self, request):
        """Valide la fin d'un chapitre : progression, recompenses et deblocage de heros."""
        payload = CompleteLevelSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        try:
            level = Level.objects.select_related("department", "unlocks_hero").get(
                id=payload.validated_data["level_id"]
            )
        except Level.DoesNotExist as exc:
            raise NotFound("Chapitre introuvable.") from exc

        score_percent = payload.validated_data["score_percent"]
        level_passed = score_percent >= level.required_score

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        progress, _ = PlayerProgress.objects.get_or_create(profile=profile, department=level.department)

        xp_awarded = 0
        coin_awarded = 0
        hero_unlocked = None

        if level_passed:
            xp_awarded = level.xp_reward
            coin_awarded = level.coin_reward
            profile.add_xp(xp_awarded)
            profile.coins += coin_awarded
            profile.save(update_fields=["coins"])

            progress.stars += 1
            progress.total_score += score_percent
            progress.current_level = level
            if level.is_boss_level:
                progress.is_completed = True
                progress.completed_at = timezone.now()
            progress.save()

            if level.unlocks_hero:
                _, created = HeroCard.objects.get_or_create(
                    profile=profile, hero=level.unlocks_hero, defaults={"unlocked_via_level": level}
                )
                if created:
                    hero_unlocked = level.unlocks_hero

        result = CompleteLevelResultSerializer(
            {
                "progress": progress,
                "level_passed": level_passed,
                "xp_awarded": xp_awarded,
                "coin_awarded": coin_awarded,
                "hero_unlocked": hero_unlocked,
            },
            context={"profile": profile},
        )
        return Response(result.data)
