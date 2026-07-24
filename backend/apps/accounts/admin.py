from datetime import timedelta

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone

from .admin_views import ONLINE_WINDOW_MINUTES
from .models import User, UserProfile


@admin.register(User)
class DefiAyitiUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_guest", "is_staff", "date_joined")
    list_filter = ("is_guest", "is_staff", "is_active")
    search_fields = ("username", "email")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user", "level", "xp", "coins", "diamonds", "trophies", "league", "win_streak",
        "department", "last_seen", "is_online",
    )
    list_filter = ("league", "department")
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user", "department")
    ordering = ("-last_seen",)

    @admin.display(boolean=True, description="En ligne")
    def is_online(self, obj) -> bool:
        if not obj.last_seen:
            return False
        return obj.last_seen >= timezone.now() - timedelta(minutes=ONLINE_WINDOW_MINUTES)
