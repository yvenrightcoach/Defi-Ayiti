import pytest
from django.utils import timezone

from apps.competition.models import PeriodWinner, ScoreEvent
from apps.competition.views import PERIOD_REWARDS, _previous_period_bounds, _week_bounds
from apps.social.models import Friend, FriendStatus


@pytest.mark.django_db
class TestLeaderboard:
    def test_national_orders_by_score_this_week(self, auth_client, make_profile):
        client, profile = auth_client
        rival = make_profile("rival")
        profile.add_xp(50)
        rival.add_xp(80)

        response = client.get("/api/v1/competition/leaderboards/", {"scope": "national", "period": "weekly"})

        assert response.status_code == 200
        usernames = [entry["profile"]["user"]["username"] for entry in response.data["entries"]]
        assert usernames[:2] == ["rival", "joueur1"]
        assert response.data["my_rank"] == 2

    def test_friends_scope_excludes_non_friends(self, auth_client, make_profile):
        client, profile = auth_client
        friend = make_profile("copain")
        stranger = make_profile("etranger")
        Friend.objects.create(requester=profile, addressee=friend, status=FriendStatus.ACCEPTED)
        profile.add_xp(10)
        friend.add_xp(20)
        stranger.add_xp(999)

        response = client.get("/api/v1/competition/leaderboards/", {"scope": "friends", "period": "weekly"})

        usernames = {entry["profile"]["user"]["username"] for entry in response.data["entries"]}
        assert usernames == {"joueur1", "copain"}

    def test_reward_matches_period(self, auth_client):
        client, _ = auth_client
        response = client.get("/api/v1/competition/leaderboards/", {"scope": "national", "period": "monthly"})
        assert response.data["reward"] == PERIOD_REWARDS["monthly"]

    def test_finalizes_previous_week_and_grants_reward(self, auth_client, make_profile):
        client, _profile = auth_client
        winner = make_profile("championne")
        prev_start, _prev_end, prev_key = _previous_period_bounds("weekly", _week_bounds(timezone.now())[0])
        event = ScoreEvent.objects.create(profile=winner, amount=100)
        ScoreEvent.objects.filter(pk=event.pk).update(created_at=prev_start + timezone.timedelta(hours=1))

        response = client.get("/api/v1/competition/leaderboards/", {"scope": "national", "period": "weekly"})

        assert response.status_code == 200
        winner.refresh_from_db()
        assert PeriodWinner.objects.filter(period_key=prev_key, profile=winner).exists()
        reward = PERIOD_REWARDS["weekly"]
        assert winner.coins == 100 + reward["coins"]
        assert winner.diamonds == reward["diamonds"]

    def test_finalization_is_idempotent(self, auth_client, make_profile):
        client, _profile = auth_client
        winner = make_profile("recidiviste")
        prev_start, _prev_end, _prev_key = _previous_period_bounds("weekly", _week_bounds(timezone.now())[0])
        event = ScoreEvent.objects.create(profile=winner, amount=100)
        ScoreEvent.objects.filter(pk=event.pk).update(created_at=prev_start + timezone.timedelta(hours=1))

        client.get("/api/v1/competition/leaderboards/", {"scope": "national", "period": "weekly"})
        client.get("/api/v1/competition/leaderboards/", {"scope": "national", "period": "weekly"})

        winner.refresh_from_db()
        reward = PERIOD_REWARDS["weekly"]
        assert winner.coins == 100 + reward["coins"]
        assert PeriodWinner.objects.filter(profile=winner).count() == 1
