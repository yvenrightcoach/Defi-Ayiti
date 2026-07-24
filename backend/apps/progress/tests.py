from unittest.mock import patch

import pytest

from apps.geography.models import Department, Level
from apps.heroes.models import Hero, HeroCard
from apps.progress.models import PlayerProgress


@pytest.fixture
def department_with_level(db):
    department = Department.objects.create(name="Ouest", slug="ouest", code="OU")
    hero = Hero.objects.create(name="Dessalines", slug="dessalines", biography="...")
    level = Level.objects.create(
        department=department,
        order=1,
        name="Les origines",
        required_score=70,
        xp_reward=50,
        coin_reward=20,
        is_boss_level=True,
        unlocks_hero=hero,
    )
    return department, level, hero


@pytest.mark.django_db
class TestCompleteLevel:
    def test_passing_score_awards_rewards_and_unlocks_hero(self, auth_client, department_with_level):
        client, profile = auth_client
        department, level, hero = department_with_level

        response = client.post(
            "/api/v1/progress/entries/complete-level/",
            {"level_id": str(level.id), "score_percent": 80},
        )

        assert response.status_code == 200
        assert response.data["level_passed"] is True
        assert response.data["xp_awarded"] == 50
        assert response.data["coin_awarded"] == 20
        assert response.data["hero_unlocked"]["id"] == str(hero.id)

        profile.refresh_from_db()
        assert profile.xp == 50
        assert profile.coins == 120  # 100 de depart + 20

        progress = PlayerProgress.objects.get(profile=profile, department=department)
        assert progress.is_completed is True  # chapitre boss
        assert HeroCard.objects.filter(profile=profile, hero=hero).count() == 1

    def test_failing_score_awards_nothing(self, auth_client, department_with_level):
        client, profile = auth_client
        _, level, _ = department_with_level

        response = client.post(
            "/api/v1/progress/entries/complete-level/",
            {"level_id": str(level.id), "score_percent": 40},
        )

        assert response.status_code == 200
        assert response.data["level_passed"] is False
        assert response.data["xp_awarded"] == 0
        assert response.data["hero_unlocked"] is None

        profile.refresh_from_db()
        assert profile.xp == 0
        assert profile.coins == 100

    def test_replaying_a_completed_level_does_not_duplicate_hero_card(self, auth_client, department_with_level):
        client, profile = auth_client
        _, level, hero = department_with_level

        client.post("/api/v1/progress/entries/complete-level/", {"level_id": str(level.id), "score_percent": 80})
        response = client.post(
            "/api/v1/progress/entries/complete-level/", {"level_id": str(level.id), "score_percent": 80}
        )

        assert response.data["hero_unlocked"] is None  # deja debloque, pas de doublon
        assert HeroCard.objects.filter(profile=profile, hero=hero).count() == 1

    def test_unknown_level_returns_404(self, auth_client):
        client, _ = auth_client
        response = client.post(
            "/api/v1/progress/entries/complete-level/",
            {"level_id": "00000000-0000-0000-0000-000000000000", "score_percent": 80},
        )
        assert response.status_code == 404


@pytest.fixture
def level_with_bonus_pool(db):
    """Un chapitre sans heros dedie, plus un heros bonus legendaire et un commun disponibles au tirage."""
    department = Department.objects.create(name="Ouest", slug="ouest", code="OU")
    level = Level.objects.create(
        department=department, order=1, name="Les origines", required_score=70, is_boss_level=True
    )
    legendary_bonus = Hero.objects.create(name="Boukman", slug="boukman", biography="...", rarity="legendary")
    common_bonus = Hero.objects.create(name="Durand", slug="durand", biography="...", rarity="common")
    return level, legendary_bonus, common_bonus


@pytest.mark.django_db
class TestBonusHeroDrop:
    def test_successful_roll_awards_a_legendary_bonus_hero(self, auth_client, level_with_bonus_pool):
        client, _ = auth_client
        level, legendary_bonus, _ = level_with_bonus_pool

        with patch("apps.progress.views.random.random", return_value=0.0):
            response = client.post(
                "/api/v1/progress/entries/complete-level/",
                {"level_id": str(level.id), "score_percent": 80},
            )

        assert response.data["hero_unlocked"]["id"] == str(legendary_bonus.id)

    def test_failed_rolls_award_no_bonus_hero(self, auth_client, level_with_bonus_pool):
        client, _ = auth_client
        level, *_ = level_with_bonus_pool

        with patch("apps.progress.views.random.random", return_value=0.99):
            response = client.post(
                "/api/v1/progress/entries/complete-level/",
                {"level_id": str(level.id), "score_percent": 80},
            )

        assert response.data["hero_unlocked"] is None

    def test_a_hero_linked_to_a_level_is_never_drawn_as_bonus(self, auth_client):
        """Un heros deja lie a un chapitre (unlocks_hero) ne doit jamais sortir du pool bonus."""
        client, _ = auth_client
        dept = Department.objects.create(name="Ouest", slug="ouest", code="OU")
        other_dept = Department.objects.create(name="Nord", slug="nord", code="ND")
        linked_hero = Hero.objects.create(name="Dessalines", slug="dessalines", biography="...", rarity="common")
        Level.objects.create(department=other_dept, order=1, name="Autre chapitre", unlocks_hero=linked_hero)
        bonus_hero = Hero.objects.create(name="Durand", slug="durand", biography="...", rarity="common")
        level = Level.objects.create(
            department=dept, order=1, name="Les origines", required_score=70, is_boss_level=True
        )

        with patch("apps.progress.views.random.random", return_value=0.0):
            response = client.post(
                "/api/v1/progress/entries/complete-level/",
                {"level_id": str(level.id), "score_percent": 80},
            )

        assert response.data["hero_unlocked"]["id"] == str(bonus_hero.id)


@pytest.mark.django_db
class TestDepartmentIsUnlocked:
    def test_first_department_is_always_unlocked(self, auth_client):
        client, _ = auth_client
        Department.objects.create(name="Ouest", slug="ouest", code="OU", order=1)
        response = client.get("/api/v1/geography/departments/")
        assert response.data["results"][0]["is_unlocked"] is True

    def test_second_department_locked_until_first_is_completed(self, auth_client):
        client, profile = auth_client
        dept1 = Department.objects.create(name="Ouest", slug="ouest", code="OU", order=1)
        dept2 = Department.objects.create(name="Nord", slug="nord", code="ND", order=2)

        response = client.get("/api/v1/geography/departments/")
        by_id = {d["id"]: d for d in response.data["results"]}
        assert by_id[str(dept2.id)]["is_unlocked"] is False

        PlayerProgress.objects.create(profile=profile, department=dept1, is_completed=True)

        response = client.get("/api/v1/geography/departments/")
        by_id = {d["id"]: d for d in response.data["results"]}
        assert by_id[str(dept2.id)]["is_unlocked"] is True
