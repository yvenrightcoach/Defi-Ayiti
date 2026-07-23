import pytest
from rest_framework.test import APIClient

from apps.battles.models import BattleRoom, RoomStatus
from apps.quiz.models import Answer, Category, Question


@pytest.fixture
def some_questions(db):
    category = Category.objects.create(name="Histoire", slug="histoire")
    questions = []
    for i in range(3):
        q = Question.objects.create(category=category, text=f"Question {i}", xp_reward=10)
        Answer.objects.create(question=q, text="bonne", is_correct=True)
        Answer.objects.create(question=q, text="mauvaise", is_correct=False)
        questions.append(q)
    return questions


@pytest.fixture
def second_client(make_profile):
    """Un deuxieme client API independant, authentifie comme un autre joueur."""
    joiner = make_profile("joueur2")
    client = APIClient()
    client.force_authenticate(user=joiner.user)
    return client, joiner


@pytest.mark.django_db
class TestBattleRoomLifecycle:
    def test_create_room_adds_host_as_participant(self, auth_client):
        client, profile = auth_client
        response = client.post("/api/v1/battles/rooms/", {"room_type": "friend", "max_players": 2})
        assert response.status_code == 201
        room = BattleRoom.objects.get(id=response.data["id"])
        assert list(room.participants.all()) == [profile]
        assert room.status == RoomStatus.WAITING
        assert len(room.room_code) == 6

    def test_join_adds_second_participant(self, auth_client, second_client):
        client, _ = auth_client
        joiner_client, _ = second_client
        room_resp = client.post("/api/v1/battles/rooms/", {"room_type": "friend", "max_players": 2})
        room_code = room_resp.data["room_code"]

        join_resp = joiner_client.post("/api/v1/battles/rooms/join/", {"room_code": room_code})

        assert join_resp.status_code == 200
        room = BattleRoom.objects.get(room_code=room_code)
        assert room.participants.count() == 2

    def test_join_full_room_fails(self, auth_client, second_client):
        client, _ = auth_client
        joiner_client, _ = second_client
        room_resp = client.post("/api/v1/battles/rooms/", {"room_type": "friend", "max_players": 1})
        room_code = room_resp.data["room_code"]

        response = joiner_client.post("/api/v1/battles/rooms/join/", {"room_code": room_code})
        assert response.status_code == 400

    def test_join_invalid_code_404(self, auth_client):
        client, _ = auth_client
        response = client.post("/api/v1/battles/rooms/join/", {"room_code": "ZZZZZZ"})
        assert response.status_code == 404


@pytest.mark.django_db
class TestMatchLifecycle:
    def test_only_host_can_start_match(self, auth_client, second_client, some_questions):
        client, _ = auth_client
        joiner_client, _ = second_client
        room_resp = client.post("/api/v1/battles/rooms/", {"room_type": "friend", "max_players": 2})
        room_id = room_resp.data["id"]
        room_code = room_resp.data["room_code"]
        joiner_client.post("/api/v1/battles/rooms/join/", {"room_code": room_code})

        response = joiner_client.post(f"/api/v1/battles/rooms/{room_id}/start/", {"question_count": 2})
        assert response.status_code == 403

    def test_start_creates_match_with_participants(self, auth_client, second_client, some_questions):
        client, host_profile = auth_client
        joiner_client, _ = second_client
        room_resp = client.post("/api/v1/battles/rooms/", {"room_type": "friend", "max_players": 2})
        room_id = room_resp.data["id"]
        room_code = room_resp.data["room_code"]
        joiner_client.post("/api/v1/battles/rooms/join/", {"room_code": room_code})

        response = client.post(f"/api/v1/battles/rooms/{room_id}/start/", {"question_count": 2})
        assert response.status_code == 201
        assert len(response.data["questions"]) == 2
        assert len(response.data["participants"]) == 2

    def test_finish_ranks_and_rewards_winner(self, auth_client, second_client, some_questions):
        client, host_profile = auth_client
        joiner_client, joiner = second_client
        room_resp = client.post("/api/v1/battles/rooms/", {"room_type": "friend", "max_players": 2})
        room_id = room_resp.data["id"]
        room_code = room_resp.data["room_code"]
        joiner_client.post("/api/v1/battles/rooms/join/", {"room_code": room_code})

        match_resp = client.post(f"/api/v1/battles/rooms/{room_id}/start/", {"question_count": 2})
        match_id = match_resp.data["id"]

        client.post(f"/api/v1/battles/matches/{match_id}/submit-score/", {"score": 20, "correct_answers": 2})
        joiner_client.post(f"/api/v1/battles/matches/{match_id}/submit-score/", {"score": 10, "correct_answers": 1})

        finish_resp = client.post(f"/api/v1/battles/matches/{match_id}/finish/")

        assert finish_resp.status_code == 200
        assert finish_resp.data["winner"] == host_profile.id

        host_profile.refresh_from_db()
        joiner.refresh_from_db()
        assert host_profile.trophies == 20
        assert host_profile.win_streak == 1
        assert joiner.win_streak == 0

        room = BattleRoom.objects.get(id=room_id)
        assert room.status == RoomStatus.FINISHED
