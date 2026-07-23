from django.contrib import admin

from .models import PlayerProgress


@admin.register(PlayerProgress)
class PlayerProgressAdmin(admin.ModelAdmin):
    list_display = ("profile", "department", "current_level", "stars", "total_score", "is_completed")
    list_filter = ("department", "is_completed")
    search_fields = ("profile__user__username",)
    autocomplete_fields = ("profile", "department", "current_level")
