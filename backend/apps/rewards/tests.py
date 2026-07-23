import pytest
from django.utils import timezone

from apps.rewards.models import Mission, PlayerMission, Purchase, ShopItem


@pytest.mark.django_db
class TestClaimMission:
    def test_claim_completed_mission_awards_rewards(self, auth_client):
        client, profile = auth_client
        mission = Mission.objects.create(
            name="Quete du jour", mission_type="answer_questions", target_value=1, xp_reward=30, coin_reward=15
        )
        player_mission = PlayerMission.objects.create(
            profile=profile, mission=mission, progress=1, is_completed=True, completed_at=timezone.now()
        )

        response = client.post(f"/api/v1/rewards/player-missions/{player_mission.id}/claim/")
        assert response.status_code == 200
        assert response.data == {"xp_awarded": 30, "coin_awarded": 15}

        profile.refresh_from_db()
        assert profile.xp == 30
        assert profile.coins == 115

        player_mission.refresh_from_db()
        assert player_mission.reward_claimed is True

    def test_cannot_claim_twice(self, auth_client):
        client, profile = auth_client
        mission = Mission.objects.create(name="Quete", mission_type="answer_questions", target_value=1)
        player_mission = PlayerMission.objects.create(
            profile=profile, mission=mission, is_completed=True, reward_claimed=True
        )

        response = client.post(f"/api/v1/rewards/player-missions/{player_mission.id}/claim/")
        assert response.status_code == 400

    def test_cannot_claim_unfinished_mission(self, auth_client):
        client, profile = auth_client
        mission = Mission.objects.create(name="Quete", mission_type="answer_questions", target_value=5)
        player_mission = PlayerMission.objects.create(profile=profile, mission=mission, progress=2)

        response = client.post(f"/api/v1/rewards/player-missions/{player_mission.id}/claim/")
        assert response.status_code == 400


@pytest.mark.django_db
class TestPurchase:
    def test_purchase_deducts_currency(self, auth_client):
        client, profile = auth_client
        item = ShopItem.objects.create(name="Avatar", item_type="avatar", price_coins=60)

        response = client.post("/api/v1/rewards/purchases/", {"shop_item_id": str(item.id)})
        assert response.status_code == 201

        profile.refresh_from_db()
        assert profile.coins == 40
        assert Purchase.objects.filter(profile=profile, shop_item=item).exists()

    def test_purchase_fails_with_insufficient_funds(self, auth_client):
        client, profile = auth_client
        item = ShopItem.objects.create(name="Avatar rare", item_type="avatar", price_coins=1000)

        response = client.post("/api/v1/rewards/purchases/", {"shop_item_id": str(item.id)})
        assert response.status_code == 400

        profile.refresh_from_db()
        assert profile.coins == 100
        assert not Purchase.objects.filter(profile=profile, shop_item=item).exists()
