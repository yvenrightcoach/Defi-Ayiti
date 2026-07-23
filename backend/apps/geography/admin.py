from django.contrib import admin

from .models import Department, Level


class LevelInline(admin.TabularInline):
    model = Level
    extra = 0
    fields = ("order", "name", "xp_reward", "coin_reward", "is_boss_level", "unlocks_hero")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "capital", "order")
    search_fields = ("name", "code", "capital")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [LevelInline]


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ("department", "order", "name", "is_boss_level", "unlocks_hero")
    list_filter = ("department", "is_boss_level")
    search_fields = ("name",)
    autocomplete_fields = ("department", "unlocks_hero")
