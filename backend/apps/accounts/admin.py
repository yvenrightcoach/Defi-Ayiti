from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserProfile


@admin.register(User)
class DefiAyitiUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_guest", "is_staff", "date_joined")
    list_filter = ("is_guest", "is_staff", "is_active")
    search_fields = ("username", "email")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user", "level", "xp", "coins", "diamonds", "trophies", "league", "win_streak", "department",
    )
    list_filter = ("league", "department")
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user", "department")
