import datetime

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
class TestClaimAdReward:
    def test_awards_coins(self, auth_client):
        client, profile = auth_client
        response = client.post("/api/v1/auth/me/claim-ad-reward/")
        assert response.status_code == 200
        assert response.data["coins_awarded"] == 30
        profile.refresh_from_db()
        assert profile.coins == 130

    def test_daily_limit_blocks_further_claims(self, auth_client):
        client, profile = auth_client
        for _ in range(5):
            response = client.post("/api/v1/auth/me/claim-ad-reward/")
            assert response.status_code == 200

        response = client.post("/api/v1/auth/me/claim-ad-reward/")
        assert response.status_code == 429
        assert response.data["coins_awarded"] == 0

        profile.refresh_from_db()
        assert profile.coins == 100 + 5 * 30

    def test_limit_resets_on_a_new_day(self, auth_client):
        client, profile = auth_client
        for _ in range(5):
            client.post("/api/v1/auth/me/claim-ad-reward/")

        profile.refresh_from_db()
        profile.ad_rewards_date -= datetime.timedelta(days=1)
        profile.save(update_fields=["ad_rewards_date"])

        response = client.post("/api/v1/auth/me/claim-ad-reward/")
        assert response.status_code == 200
        assert response.data["coins_awarded"] == 30

    def test_requires_authentication(self, api_client):
        response = api_client.post("/api/v1/auth/me/claim-ad-reward/")
        assert response.status_code == 401
