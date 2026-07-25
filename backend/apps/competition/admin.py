from django.contrib import admin

from .models import Event, PeriodWinner, ScoreEvent, Season


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


@admin.register(ScoreEvent)
class ScoreEventAdmin(admin.ModelAdmin):
    list_display = ("profile", "amount", "created_at")
    list_filter = ("created_at",)
    search_fields = ("profile__user__username",)
    autocomplete_fields = ("profile",)


@admin.register(PeriodWinner)
class PeriodWinnerAdmin(admin.ModelAdmin):
    list_display = ("period_key", "period", "profile", "score", "coins_awarded", "diamonds_awarded", "granted_at")
    list_filter = ("period",)
    search_fields = ("profile__user__username", "period_key")
    autocomplete_fields = ("profile",)
