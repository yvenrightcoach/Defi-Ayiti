import pytest
from rest_framework.test import APIClient

from apps.social.models import Friend, FriendStatus


@pytest.fixture
def second_client(make_profile):
    """Un deuxieme client API independant, authentifie comme un autre joueur."""
    other = make_profile("ami1")
    client = APIClient()
    client.force_authenticate(user=other.user)
    return client, other


@pytest.mark.django_db
class TestFriendRequests:
    def test_send_request(self, auth_client, second_client):
        client, profile = auth_client
        _, addressee = second_client
        response = client.post("/api/v1/social/friends/", {"addressee_id": str(addressee.id)})
        assert response.status_code == 201
        assert Friend.objects.filter(requester=profile, addressee=addressee, status=FriendStatus.PENDING).exists()

    def test_cannot_send_duplicate_request(self, auth_client, second_client):
        client, _ = auth_client
        _, addressee = second_client
        client.post("/api/v1/social/friends/", {"addressee_id": str(addressee.id)})
        response = client.post("/api/v1/social/friends/", {"addressee_id": str(addressee.id)})
        assert response.status_code == 400

    def test_cannot_add_self(self, auth_client):
        client, profile = auth_client
        response = client.post("/api/v1/social/friends/", {"addressee_id": str(profile.id)})
        assert response.status_code == 400

    def test_only_addressee_can_accept(self, auth_client, second_client):
        client, _ = auth_client
        addressee_client, addressee = second_client
        req_resp = client.post("/api/v1/social/friends/", {"addressee_id": str(addressee.id)})
        friend_id = req_resp.data["id"]

        response = client.post(f"/api/v1/social/friends/{friend_id}/accept/")
        assert response.status_code == 403

        response = addressee_client.post(f"/api/v1/social/friends/{friend_id}/accept/")
        assert response.status_code == 200
        assert response.data["status"] == FriendStatus.ACCEPTED

    def test_accepted_friends_appear_in_friends_list(self, auth_client, second_client):
        client, requester = auth_client
        addressee_client, addressee = second_client
        req_resp = client.post("/api/v1/social/friends/", {"addressee_id": str(addressee.id)})
        addressee_client.post(f"/api/v1/social/friends/{req_resp.data['id']}/accept/")

        response = client.get("/api/v1/social/friends/friends/")
        assert response.status_code == 200
        usernames = [p["user"]["username"] for p in response.data]
        assert addressee.user.username in usernames

    def test_declined_request_does_not_appear_in_friends_list(self, auth_client, second_client):
        client, requester = auth_client
        addressee_client, addressee = second_client
        req_resp = client.post("/api/v1/social/friends/", {"addressee_id": str(addressee.id)})
        addressee_client.post(f"/api/v1/social/friends/{req_resp.data['id']}/decline/")

        response = client.get("/api/v1/social/friends/friends/")
        assert response.data == []
