from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "competition"

router = DefaultRouter()
router.register("seasons", views.SeasonViewSet, basename="season")
router.register("events", views.EventViewSet, basename="event")
router.register("leaderboards", views.LeaderboardViewSet, basename="leaderboard")

urlpatterns = [
    path("", include(router.urls)),
]
