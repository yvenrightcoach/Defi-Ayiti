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
    StakeLevelResultSerializer,
    StakeLevelSerializer,
)

# Chance (par chapitre reussi) de recevoir en bonus un heros non lie a un
# chapitre precis. Verifiees de la plus rare a la plus commune : un heros
# legendaire reste volontairement tres difficile a obtenir, et meme un
# commun n'est pas garanti a chaque victoire (aucun heros bonus la majorite
# du temps), pour que la collection reste un objectif long-terme.
BONUS_HERO_DROP_RATES = {
    "legendary": 0.02,
    "epic": 0.08,
    "rare": 0.18,
    "common": 0.35,
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

    @extend_schema(request=StakeLevelSerializer, responses=StakeLevelResultSerializer)
    @action(detail=False, methods=["post"], url_path="stake-level")
    def stake_level(self, request):
        """
        Mise obligatoire en pieces avant de tenter un chapitre : le joueur ne
        peut pas jouer sans miser, et perd sa mise en cas d'echec. Empeche
        aussi de miser sur un departement encore verrouille.
        """
        payload = StakeLevelSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        try:
            level = Level.objects.select_related("department").get(id=payload.validated_data["level_id"])
        except Level.DoesNotExist as exc:
            raise NotFound("Chapitre introuvable.") from exc

        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        if not self._department_unlocked(profile, level.department):
            return Response({"detail": "Ce departement est encore verrouille."}, status=403)

        if profile.coins < level.stake_cost:
            return Response(
                {
                    "detail": "Pas assez de pieces pour miser sur ce chapitre.",
                    "stake_cost": level.stake_cost,
                    "coins": profile.coins,
                },
                status=402,
            )

        progress, _ = PlayerProgress.objects.get_or_create(profile=profile, department=level.department)
        profile.coins -= level.stake_cost
        profile.save(update_fields=["coins"])
        progress.pending_stake = level.stake_cost
        progress.save(update_fields=["pending_stake"])

        result = StakeLevelResultSerializer({"stake_cost": level.stake_cost, "coins_remaining": profile.coins})
        return Response(result.data)

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
        stake_refunded = 0
        stake_lost = False

        staked = progress.pending_stake
        coins_dirty = False
        progress_dirty = False

        if staked:
            progress.pending_stake = 0
            progress_dirty = True

        if level_passed:
            xp_awarded = level.xp_reward
            coin_awarded = level.coin_reward
            profile.add_xp(xp_awarded)
            profile.coins += coin_awarded
            coins_dirty = True

            if staked:
                profile.coins += staked
                stake_refunded = staked

            progress.stars += 1
            progress.total_score += score_percent
            progress.current_level = level
            if level.is_boss_level:
                progress.is_completed = True
                progress.completed_at = timezone.now()
            progress_dirty = True

            if level.unlocks_hero:
                _, created = HeroCard.objects.get_or_create(
                    profile=profile, hero=level.unlocks_hero, defaults={"unlocked_via_level": level}
                )
                if created:
                    hero_unlocked = level.unlocks_hero

            if hero_unlocked is None:
                hero_unlocked = self._roll_bonus_hero(profile)
        elif staked:
            stake_lost = True

        if coins_dirty:
            profile.save(update_fields=["coins"])
        if progress_dirty:
            progress.save()

        result = CompleteLevelResultSerializer(
            {
                "progress": progress,
                "level_passed": level_passed,
                "xp_awarded": xp_awarded,
                "coin_awarded": coin_awarded,
                "hero_unlocked": hero_unlocked,
                "stake_refunded": stake_refunded,
                "stake_lost": stake_lost,
            },
            context={"profile": profile},
        )
        return Response(result.data)

    @staticmethod
    def _department_unlocked(profile, department):
        """Meme regle que DepartmentSerializer.get_is_unlocked : le premier
        departement est libre, les suivants exigent le precedent termine."""
        if department.order <= 1:
            return True
        return PlayerProgress.objects.filter(
            profile=profile, department__order=department.order - 1, is_completed=True
        ).exists()

    @staticmethod
    def _roll_bonus_hero(profile):
        """
        Tire au sort un heros 'bonus' (non lie a un chapitre precis) a
        ajouter a la collection du joueur. Les raretes sont testees de la
        plus rare a la plus commune ; des qu'un tirage reussit et qu'un
        heros de cette rarete reste a debloquer, il est accorde.

        Chaque heros bonus a aussi un niveau de joueur minimum (voir
        Hero.unlock_level, cf. seed_content) : les meilleures raretes restent
        hors de portee tant que le joueur n'a pas assez progresse, ce qui
        transforme la collection en objectif de progression visible plutot
        qu'en pure loterie des le niveau 1.
        """
        owned_ids = HeroCard.objects.filter(profile=profile).values_list("hero_id", flat=True)
        for rarity, chance in BONUS_HERO_DROP_RATES.items():
            if random.random() > chance:
                continue
            candidates = list(
                Hero.objects.filter(
                    rarity=rarity, unlocked_by_levels__isnull=True, unlock_level__lte=profile.level
                ).exclude(id__in=owned_ids)
            )
            if candidates:
                hero = random.choice(candidates)
                HeroCard.objects.create(profile=profile, hero=hero)
                return hero
        return None
