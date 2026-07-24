import pytest

from apps.geography.models import Department, Level
from apps.quiz.models import Answer, Category, Question
from apps.rewards.models import Mission, PlayerMission


@pytest.fixture
def question_with_answers(db):
    category = Category.objects.create(name="Histoire", slug="histoire")
    question = Question.objects.create(
        category=category,
        text="En quelle annee Haiti a-t-il obtenu son independance ?",
        xp_reward=10,
        explanation="1804.",
    )
    correct = Answer.objects.create(question=question, text="1804", is_correct=True, order=0)
    wrong = Answer.objects.create(question=question, text="1789", is_correct=False, order=1)
    return question, correct, wrong


@pytest.mark.django_db
class TestQuestionList:
    def test_correct_answer_and_explanation_are_never_exposed(self, auth_client, question_with_answers):
        client, _ = auth_client
        question, *_ = question_with_answers
        response = client.get(f"/api/v1/quiz/questions/{question.id}/")
        assert response.status_code == 200
        assert "explanation" not in response.data
        for answer in response.data["answers"]:
            assert "is_correct" not in answer


@pytest.mark.django_db
class TestSubmitAnswer:
    def test_correct_answer_awards_xp(self, auth_client, question_with_answers):
        client, profile = auth_client
        question, correct, _ = question_with_answers
        response = client.post(f"/api/v1/quiz/questions/{question.id}/submit/", {"answer_ids": [str(correct.id)]})
        assert response.status_code == 200
        assert response.data["is_correct"] is True
        assert response.data["xp_awarded"] == 10
        assert response.data["explanation"] == "1804."

        profile.refresh_from_db()
        assert profile.xp == 10

    def test_incorrect_answer_awards_no_xp(self, auth_client, question_with_answers):
        client, profile = auth_client
        question, _, wrong = question_with_answers
        response = client.post(f"/api/v1/quiz/questions/{question.id}/submit/", {"answer_ids": [str(wrong.id)]})
        assert response.status_code == 200
        assert response.data["is_correct"] is False
        assert response.data["xp_awarded"] == 0

        profile.refresh_from_db()
        assert profile.xp == 0

    def test_correct_answer_progresses_daily_mission(self, auth_client, question_with_answers):
        client, profile = auth_client
        question, correct, _ = question_with_answers
        mission = Mission.objects.create(
            name="Repondre a 5 questions", mission_type="answer_questions", target_value=5
        )
        player_mission = PlayerMission.objects.create(profile=profile, mission=mission)

        client.post(f"/api/v1/quiz/questions/{question.id}/submit/", {"answer_ids": [str(correct.id)]})

        player_mission.refresh_from_db()
        assert player_mission.progress == 1
        assert player_mission.is_completed is False

    def test_mission_marked_completed_when_target_reached(self, auth_client, question_with_answers):
        client, profile = auth_client
        question, correct, _ = question_with_answers
        mission = Mission.objects.create(name="Repondre a 1 question", mission_type="answer_questions", target_value=1)
        player_mission = PlayerMission.objects.create(profile=profile, mission=mission)

        client.post(f"/api/v1/quiz/questions/{question.id}/submit/", {"answer_ids": [str(correct.id)]})

        player_mission.refresh_from_db()
        assert player_mission.is_completed is True
        assert player_mission.reward_claimed is False


@pytest.fixture
def level_with_pool(db):
    """Un chapitre avec 3 questions dediees + 40 questions generales (sans niveau ni departement)."""
    category = Category.objects.create(name="Histoire", slug="histoire")
    department = Department.objects.create(name="Ouest", slug="ouest", code="OU")
    level = Level.objects.create(department=department, order=1, name="Les origines")

    for i in range(3):
        Question.objects.create(category=category, level=level, department=department, text=f"Question niveau {i}")
    for i in range(40):
        Question.objects.create(category=category, text=f"Question generale {i}")

    return level


@pytest.mark.django_db
class TestQuestionSession:
    def test_caps_at_30_questions(self, auth_client, level_with_pool):
        client, _ = auth_client
        response = client.get(f"/api/v1/quiz/questions/session/?level={level_with_pool.id}")
        assert response.status_code == 200
        assert len(response.data) == 30

    def test_combines_level_and_general_pool(self, auth_client, level_with_pool):
        client, _ = auth_client
        response = client.get(f"/api/v1/quiz/questions/session/?level={level_with_pool.id}")
        texts = {q["text"] for q in response.data}
        assert any(t.startswith("Question niveau") for t in texts)
        assert any(t.startswith("Question generale") for t in texts)

    def test_random_order_varies_between_calls(self, auth_client, level_with_pool):
        client, _ = auth_client
        first = [q["id"] for q in client.get(f"/api/v1/quiz/questions/session/?level={level_with_pool.id}").data]
        second = [q["id"] for q in client.get(f"/api/v1/quiz/questions/session/?level={level_with_pool.id}").data]
        assert first != second

    def test_without_level_uses_full_active_pool(self, auth_client, level_with_pool):
        client, _ = auth_client
        response = client.get("/api/v1/quiz/questions/session/")
        assert response.status_code == 200
        assert len(response.data) == 30
