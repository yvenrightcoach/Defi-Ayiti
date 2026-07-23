from django.contrib import admin

from .models import BattleRoom, Match, MatchParticipant


class MatchParticipantInline(admin.TabularInline):
    model = MatchParticipant
    extra = 0
    fields = ("profile", "score", "correct_answers", "rank")
    autocomplete_fields = ("profile",)


@admin.register(BattleRoom)
class BattleRoomAdmin(admin.ModelAdmin):
    list_display = ("room_code", "room_type", "host", "max_players", "status", "created_at")
    list_filter = ("room_type", "status")
    search_fields = ("room_code", "host__user__username")
    autocomplete_fields = ("host", "participants", "rematch_of")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "round_number", "status", "winner", "started_at", "ended_at")
    list_filter = ("status",)
    search_fields = ("room__room_code",)
    autocomplete_fields = ("room", "winner")
    inlines = [MatchParticipantInline]
