from django.contrib import admin

from .models import Event, Leaderboard, Season


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("name", "theme", "start_date", "end_date", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "theme")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "season", "start_at", "end_at", "is_active")
    list_filter = ("is_active", "season")
    search_fields = ("name",)
    autocomplete_fields = ("season", "reward")


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ("scope", "period", "department", "season", "profile", "rank", "score")
    list_filter = ("scope", "period", "department", "season")
    search_fields = ("profile__user__username",)
    autocomplete_fields = ("department", "season", "profile")
