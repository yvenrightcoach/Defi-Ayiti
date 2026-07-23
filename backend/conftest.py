import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User, UserProfile


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def make_profile(db):
    """Factory : cree un User + UserProfile (le signal cree deja le profil, on le recupere)."""

    def _make(username="joueur", **profile_fields):
        user = User.objects.create_user(username=username, email=f"{username}@test.local", password="pass1234")
        profile = UserProfile.objects.get(user=user)
        if profile_fields:
            for key, value in profile_fields.items():
                setattr(profile, key, value)
            profile.save()
        return profile

    return _make


@pytest.fixture
def auth_client(api_client, make_profile):
    """Client API authentifie (force_authenticate) avec un profil pret a l'emploi."""
    profile = make_profile("joueur1")
    api_client.force_authenticate(user=profile.user)
    return api_client, profile
