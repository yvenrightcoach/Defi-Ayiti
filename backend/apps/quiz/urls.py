from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "quiz"

router = DefaultRouter()
router.register("categories", views.CategoryViewSet, basename="category")
router.register("questions", views.QuestionViewSet, basename="question")

urlpatterns = [
    path("", include(router.urls)),
]
