from django.contrib import admin

from .models import Friend


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ("requester", "addressee", "status", "created_at", "responded_at")
    list_filter = ("status",)
    search_fields = ("requester__user__username", "addressee__user__username")
    autocomplete_fields = ("requester", "addressee")
