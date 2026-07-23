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
