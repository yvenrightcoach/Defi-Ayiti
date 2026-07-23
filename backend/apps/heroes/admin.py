from django.contrib import admin

from .models import Hero, HeroCard


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "rarity", "unlock_level", "order")
    list_filter = ("rarity", "department")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("department",)


@admin.register(HeroCard)
class HeroCardAdmin(admin.ModelAdmin):
    list_display = ("profile", "hero", "unlocked_at")
    list_filter = ("hero",)
    search_fields = ("profile__user__username", "hero__name")
    autocomplete_fields = ("profile", "hero", "unlocked_via_level")
