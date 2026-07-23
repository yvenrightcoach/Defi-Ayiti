from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "heroes"

router = DefaultRouter()
router.register("heroes", views.HeroViewSet, basename="hero")
router.register("cards", views.HeroCardViewSet, basename="herocard")

urlpatterns = [
    path("", include(router.urls)),
]
