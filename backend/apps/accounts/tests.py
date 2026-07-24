import pytest
from django.urls import reverse

from apps.accounts.models import User, UserProfile


@pytest.mark.django_db
class TestUserProfileSignal:
    def test_profile_created_automatically_on_user_creation(self):
        user = User.objects.create_user(username="nouveau", email="nouveau@test.local", password="pass1234")
        profile = UserProfile.objects.get(user=user)
        assert profile.coins == 100
        assert profile.level == 1
        assert profile.league == "bronze"


@pytest.mark.django_db
class TestGuestLogin:
    def test_creates_guest_user_and_returns_tokens(self, api_client):
        response = api_client.post(reverse("accounts:guest-login"))
        assert response.status_code == 201
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["is_guest"] is True

        user = User.objects.get(id=response.data["user"]["id"])
        assert user.is_guest is True
        assert UserProfile.objects.filter(user=user).exists()

    def test_disabled_when_setting_off(self, api_client, settings):
        settings.GUEST_MODE_ENABLED = False
        response = api_client.post(reverse("accounts:guest-login"))
        assert response.status_code == 403


@pytest.mark.django_db
class TestMeEndpoint:
    def test_requires_authentication(self, api_client):
        response = api_client.get("/api/v1/auth/me/")
        assert response.status_code == 401

    def test_returns_own_profile(self, auth_client):
        client, profile = auth_client
        response = client.get("/api/v1/auth/me/")
        assert response.status_code == 200
        assert response.data["user"]["username"] == profile.user.username
        assert response.data["coins"] == 100

    def test_update_avatar_and_department(self, auth_client):
        client, profile = auth_client
        response = client.patch("/api/v1/auth/me/", {"avatar_url": "https://example.com/a.png"})
        assert response.status_code == 200
        profile.refresh_from_db()
        assert profile.avatar_url == "https://example.com/a.png"

    def test_cannot_update_readonly_fields(self, auth_client):
        client, profile = auth_client
        client.patch("/api/v1/auth/me/", {"coins": 99999, "xp": 99999})
        profile.refresh_from_db()
        assert profile.coins == 100
        assert profile.xp == 0


@pytest.mark.django_db
class TestConvertDiamondsToCoins:
    def test_converts_diamonds_into_coins(self, auth_client):
        client, profile = auth_client
        profile.diamonds = 50
        profile.save(update_fields=["diamonds"])

        response = client.post("/api/v1/auth/me/convert-diamonds/", {"diamonds": 20})

        assert response.status_code == 200
        assert response.data["diamonds"] == 30
        assert response.data["coins"] == 300  # 100 de depart + 20*10

        profile.refresh_from_db()
        assert profile.diamonds == 30
        assert profile.coins == 300

    def test_fails_when_not_enough_diamonds(self, auth_client):
        client, profile = auth_client

        response = client.post("/api/v1/auth/me/convert-diamonds/", {"diamonds": 5})

        assert response.status_code == 400
        profile.refresh_from_db()
        assert profile.coins == 100
        assert profile.diamonds == 0

    def test_rejects_non_positive_amount(self, auth_client):
        client, _ = auth_client
        response = client.post("/api/v1/auth/me/convert-diamonds/", {"diamonds": 0})
        assert response.status_code == 400

    def test_requires_authentication(self, api_client):
        response = api_client.post("/api/v1/auth/me/convert-diamonds/", {"diamonds": 5})
        assert response.status_code == 401
