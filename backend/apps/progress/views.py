"""Vues DRF de l'app 'progress'."""
import random

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from apps.accounts.models import UserProfile
from apps.geography.models import Level
from apps.heroes.models import Hero, HeroCard

from .models import PlayerProgress
from .serializers import (
    CompleteLevelResultSerializer,
    CompleteLevelSerializer,
    PlayerProgressSerializer,
)

# Chance (par chapitre reussi) de recevoir en bonus un heros non lie a un
# chapitre precis. Verifiees de la plus rare a la plus commune : un heros
# legendaire reste volontairement difficile a obtenir.
BONUS_HERO_DROP_RATES = {
    "legendary": 0.05,
    "epic": 0.15,
    "rare": 0.30,
    "common": 0.60,
}


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

            if hero_unlocked is None:
                hero_unlocked = self._roll_bonus_hero(profile)

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

    @staticmethod
    def _roll_bonus_hero(profile):
        """
        Tire au sort un heros 'bonus' (non lie a un chapitre precis) a
        ajouter a la collection du joueur. Les raretes sont testees de la
        plus rare a la plus commune ; des qu'un tirage reussit et qu'un
        heros de cette rarete reste a debloquer, il est accorde.
        """
        owned_ids = HeroCard.objects.filter(profile=profile).values_list("hero_id", flat=True)
        for rarity, chance in BONUS_HERO_DROP_RATES.items():
            if random.random() > chance:
                continue
            candidates = list(
                Hero.objects.filter(rarity=rarity, unlocked_by_levels__isnull=True).exclude(id__in=owned_ids)
            )
            if candidates:
                hero = random.choice(candidates)
                HeroCard.objects.create(profile=profile, hero=hero)
                return hero
        return None
