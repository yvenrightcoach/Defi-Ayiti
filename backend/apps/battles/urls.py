from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "battles"

router = DefaultRouter()
router.register("rooms", views.BattleRoomViewSet, basename="battleroom")
router.register("matches", views.MatchViewSet, basename="match")

urlpatterns = [
    path("", include(router.urls)),
]
