from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "geography"

router = DefaultRouter()
router.register("departments", views.DepartmentViewSet, basename="department")
router.register("levels", views.LevelViewSet, basename="level")

urlpatterns = [
    path("", include(router.urls)),
]
