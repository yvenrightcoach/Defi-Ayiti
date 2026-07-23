from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "progress"

router = DefaultRouter()
router.register("entries", views.PlayerProgressViewSet, basename="progress")

urlpatterns = [
    path("", include(router.urls)),
]
