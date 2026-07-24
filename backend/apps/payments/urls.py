from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "payments"

router = DefaultRouter()
router.register("packs", views.DiamondPackViewSet, basename="diamond-pack")

urlpatterns = [
    path("checkout/stripe/", views.CreateStripeCheckoutView.as_view(), name="stripe-checkout"),
    path("webhook/stripe/", views.StripeWebhookView.as_view(), name="stripe-webhook"),
    path("", include(router.urls)),
]
