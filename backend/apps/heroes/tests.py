import pytest

from apps.geography.models import Department
from apps.heroes.models import Hero, HeroCard


@pytest.mark.django_db
class TestHeroCatalog:
    def test_is_unlocked_reflects_the_connected_profile(self, auth_client):
        client, profile = auth_client
        hero = Hero.objects.create(name="Dessalines", slug="dessalines", biography="...")

        response = client.get("/api/v1/heroes/heroes/")
        assert response.data["results"][0]["is_unlocked"] is False

        HeroCard.objects.create(profile=profile, hero=hero)
        response = client.get("/api/v1/heroes/heroes/")
        assert response.data["results"][0]["is_unlocked"] is True

    def test_department_name_is_exposed_for_chapter_heroes(self, auth_client):
        client, _ = auth_client
        department = Department.objects.create(name="Ouest", slug="ouest", code="OU")
        Hero.objects.create(name="Catherine Flon", slug="catherine-flon", biography="...", department=department)

        response = client.get("/api/v1/heroes/heroes/")

        assert response.data["results"][0]["department_name"] == "Ouest"

    def test_department_name_is_blank_for_bonus_heroes(self, auth_client):
        client, _ = auth_client
        Hero.objects.create(name="Oswald Durand", slug="oswald-durand", biography="...")

        response = client.get("/api/v1/heroes/heroes/")

        assert response.data["results"][0]["department_name"] == ""
