from unittest.mock import Mock, patch

import pytest

from apps.payments.models import DiamondPack, DiamondPurchase, PaymentStatus


@pytest.fixture
def pack(db):
    return DiamondPack.objects.create(name="Petit sac", diamonds_amount=100, price_usd_cents=299)


@pytest.mark.django_db
class TestDiamondPackList:
    def test_lists_only_active_packs(self, auth_client, pack):
        client, _ = auth_client
        DiamondPack.objects.create(name="Pack retire", diamonds_amount=50, price_usd_cents=99, is_active=False)

        response = client.get("/api/v1/payments/packs/")
        assert response.status_code == 200
        names = {p["name"] for p in response.data["results"]}
        assert pack.name in names
        assert "Pack retire" not in names


@pytest.mark.django_db
class TestCreateStripeCheckout:
    def test_fails_cleanly_when_stripe_not_configured(self, auth_client, pack, settings):
        settings.STRIPE_SECRET_KEY = ""
        client, _ = auth_client
        response = client.post("/api/v1/payments/checkout/stripe/", {"pack_id": str(pack.id)})
        assert response.status_code == 400

    def test_creates_pending_purchase_and_returns_checkout_url(self, auth_client, pack, settings):
        settings.STRIPE_SECRET_KEY = "sk_test_fake"
        client, profile = auth_client

        fake_session = Mock(id="cs_test_123", url="https://checkout.stripe.com/pay/cs_test_123")
        with patch("apps.payments.views.stripe.checkout.Session.create", return_value=fake_session) as create_mock:
            response = client.post("/api/v1/payments/checkout/stripe/", {"pack_id": str(pack.id)})

        assert response.status_code == 200
        assert response.data["checkout_url"] == "https://checkout.stripe.com/pay/cs_test_123"
        create_mock.assert_called_once()

        purchase = DiamondPurchase.objects.get(provider_reference="cs_test_123")
        assert purchase.profile == profile
        assert purchase.pack == pack
        assert purchase.status == PaymentStatus.PENDING
        assert purchase.diamonds_credited is False

    def test_unknown_pack_returns_404(self, auth_client, settings):
        settings.STRIPE_SECRET_KEY = "sk_test_fake"
        client, _ = auth_client
        response = client.post(
            "/api/v1/payments/checkout/stripe/", {"pack_id": "00000000-0000-0000-0000-000000000000"}
        )
        assert response.status_code == 404

    def test_requires_authentication(self, api_client, pack):
        response = api_client.post("/api/v1/payments/checkout/stripe/", {"pack_id": str(pack.id)})
        assert response.status_code == 401


@pytest.mark.django_db
class TestStripeWebhook:
    def _fake_event(self, session_id):
        return {"type": "checkout.session.completed", "data": {"object": {"id": session_id}}}

    def test_invalid_signature_returns_400(self, api_client):
        with patch("apps.payments.views.stripe.Webhook.construct_event", side_effect=ValueError("bad payload")):
            response = api_client.post(
                "/api/v1/payments/webhook/stripe/", data=b"{}", content_type="application/json"
            )
        assert response.status_code == 400

    def test_credits_diamonds_on_completed_session(self, auth_client, pack):
        client, profile = auth_client
        purchase = DiamondPurchase.objects.create(
            profile=profile, pack=pack, provider="stripe", provider_reference="cs_test_456"
        )
        starting_diamonds = profile.diamonds

        with patch(
            "apps.payments.views.stripe.Webhook.construct_event",
            return_value=self._fake_event("cs_test_456"),
        ):
            response = client.post(
                "/api/v1/payments/webhook/stripe/", data=b"{}", content_type="application/json"
            )

        assert response.status_code == 200
        purchase.refresh_from_db()
        profile.refresh_from_db()
        assert purchase.status == PaymentStatus.PAID
        assert purchase.diamonds_credited is True
        assert profile.diamonds == starting_diamonds + pack.diamonds_amount

    def test_does_not_double_credit_on_replayed_event(self, auth_client, pack):
        client, profile = auth_client
        purchase = DiamondPurchase.objects.create(
            profile=profile, pack=pack, provider="stripe", provider_reference="cs_test_789"
        )
        starting_diamonds = profile.diamonds

        with patch(
            "apps.payments.views.stripe.Webhook.construct_event",
            return_value=self._fake_event("cs_test_789"),
        ):
            client.post("/api/v1/payments/webhook/stripe/", data=b"{}", content_type="application/json")
            client.post("/api/v1/payments/webhook/stripe/", data=b"{}", content_type="application/json")

        profile.refresh_from_db()
        assert profile.diamonds == starting_diamonds + pack.diamonds_amount

    def test_unknown_session_id_is_ignored(self, api_client):
        with patch(
            "apps.payments.views.stripe.Webhook.construct_event",
            return_value=self._fake_event("cs_does_not_exist"),
        ):
            response = api_client.post(
                "/api/v1/payments/webhook/stripe/", data=b"{}", content_type="application/json"
            )
        assert response.status_code == 200
