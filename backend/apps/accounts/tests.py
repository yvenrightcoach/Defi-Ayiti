from datetime import timedelta
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

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


@pytest.mark.django_db
class TestEnsureAdminCommand:
    def test_creates_superuser_from_env_vars(self, monkeypatch):
        monkeypatch.setenv("ADMIN_USERNAME", "root")
        monkeypatch.setenv("ADMIN_EMAIL", "root@defi-ayiti.local")
        monkeypatch.setenv("ADMIN_PASSWORD", "s3cret-pass")

        call_command("ensure_admin")

        admin = User.objects.get(username="root")
        assert admin.is_superuser is True
        assert admin.is_staff is True
        assert admin.check_password("s3cret-pass")

    def test_noop_when_env_vars_missing(self, monkeypatch):
        monkeypatch.delenv("ADMIN_USERNAME", raising=False)
        monkeypatch.delenv("ADMIN_EMAIL", raising=False)
        monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

        call_command("ensure_admin")

        assert User.objects.count() == 0

    def test_does_not_recreate_or_reset_existing_admin(self, monkeypatch):
        monkeypatch.setenv("ADMIN_USERNAME", "root")
        monkeypatch.setenv("ADMIN_EMAIL", "root@defi-ayiti.local")
        monkeypatch.setenv("ADMIN_PASSWORD", "first-password")
        call_command("ensure_admin")

        monkeypatch.setenv("ADMIN_PASSWORD", "second-password")
        call_command("ensure_admin")

        assert User.objects.filter(username="root").count() == 1
        admin = User.objects.get(username="root")
        assert admin.check_password("first-password")


@pytest.mark.django_db
class TestLastSeenTracking:
    def test_updates_last_seen_on_authenticated_request(self, auth_client):
        client, profile = auth_client
        assert profile.last_seen is None

        client.get("/api/v1/auth/me/")

        profile.refresh_from_db()
        assert profile.last_seen is not None

    def test_does_not_update_again_within_the_interval(self, auth_client):
        client, profile = auth_client
        client.get("/api/v1/auth/me/")
        profile.refresh_from_db()
        first_seen = profile.last_seen

        client.get("/api/v1/auth/me/")
        profile.refresh_from_db()
        assert profile.last_seen == first_seen

    def test_updates_again_after_the_interval_elapses(self, auth_client):
        client, profile = auth_client
        client.get("/api/v1/auth/me/")
        profile.refresh_from_db()
        first_seen = profile.last_seen

        future = timezone.now() + timedelta(minutes=2)
        with patch("apps.accounts.middleware.timezone.now", return_value=future):
            client.get("/api/v1/auth/me/")

        profile.refresh_from_db()
        assert profile.last_seen > first_seen


@pytest.mark.django_db
class TestAdminDashboard:
    def test_anonymous_is_redirected_to_login(self, client):
        response = client.get("/admin/dashboard/")
        assert response.status_code == 302

    def test_staff_non_superuser_is_denied(self, client):
        staff = User.objects.create_user(
            username="staff1", email="staff1@test.local", password="pass1234", is_staff=True
        )
        client.force_login(staff)
        response = client.get("/admin/dashboard/")
        assert response.status_code == 302

    def test_superuser_can_view_dashboard(self, client):
        admin = User.objects.create_superuser(username="root", email="root@test.local", password="pass1234")
        client.force_login(admin)
        response = client.get("/admin/dashboard/")
        assert response.status_code == 200
        assert b"Tableau de bord" in response.content
