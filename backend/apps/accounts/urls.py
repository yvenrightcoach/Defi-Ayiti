from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "accounts"

router = DefaultRouter()
router.register("profiles", views.UserProfileViewSet, basename="profile")

urlpatterns = [
    # Email/mot de passe (dj-rest-auth : login, logout, password reset, JWT refresh)
    path("", include("dj_rest_auth.urls")),
    path("register/", include("dj_rest_auth.registration.urls")),
    # Google / Facebook (django-allauth social + dj-rest-auth social login)
    path("social/", include("allauth.socialaccount.urls")),
    # Mode invite
    path("guest/", views.GuestLoginView.as_view(), name="guest-login"),
    # Profil de jeu de l'utilisateur connecte
    path("me/", views.MeProfileView.as_view(), name="me"),
    path("", include(router.urls)),
]
