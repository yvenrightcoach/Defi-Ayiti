from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "rewards"

router = DefaultRouter()
router.register("rewards", views.RewardViewSet, basename="reward")
router.register("achievements", views.AchievementViewSet, basename="achievement")
router.register("player-achievements", views.PlayerAchievementViewSet, basename="playerachievement")
router.register("missions", views.MissionViewSet, basename="mission")
router.register("player-missions", views.PlayerMissionViewSet, basename="playermission")
router.register("shop-items", views.ShopItemViewSet, basename="shopitem")
router.register("purchases", views.PurchaseViewSet, basename="purchase")

urlpatterns = [
    path("", include(router.urls)),
]
