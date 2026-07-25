from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "competition"

router = DefaultRouter()
router.register("seasons", views.SeasonViewSet, basename="season")
router.register("events", views.EventViewSet, basename="event")

urlpatterns = [
    path("leaderboards/", views.LeaderboardView.as_view(), name="leaderboard"),
    path("", include(router.urls)),
]
