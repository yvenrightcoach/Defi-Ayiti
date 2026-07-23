from django.contrib import admin

from .models import (
    Achievement,
    Mission,
    PlayerAchievement,
    PlayerMission,
    Purchase,
    Reward,
    ShopItem,
)


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ("name", "reward_type", "coins_amount", "diamonds_amount", "xp_amount", "grants_hero")
    list_filter = ("reward_type",)
    search_fields = ("name",)
    autocomplete_fields = ("grants_hero",)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("name", "criteria_type", "criteria_value", "reward")
    list_filter = ("criteria_type",)
    search_fields = ("name",)
    autocomplete_fields = ("reward",)


@admin.register(PlayerAchievement)
class PlayerAchievementAdmin(admin.ModelAdmin):
    list_display = ("profile", "achievement", "progress", "unlocked_at")
    list_filter = ("achievement",)
    search_fields = ("profile__user__username",)
    autocomplete_fields = ("profile", "achievement")


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ("name", "mission_type", "target_value", "xp_reward", "coin_reward", "is_daily", "is_active")
    list_filter = ("mission_type", "is_daily", "is_active")
    search_fields = ("name",)


@admin.register(PlayerMission)
class PlayerMissionAdmin(admin.ModelAdmin):
    list_display = ("profile", "mission", "assigned_date", "progress", "is_completed")
    list_filter = ("mission", "is_completed", "assigned_date")
    search_fields = ("profile__user__username",)
    autocomplete_fields = ("profile", "mission")


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ("name", "item_type", "price_coins", "price_diamonds", "is_available")
    list_filter = ("item_type", "is_available")
    search_fields = ("name",)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("profile", "shop_item", "price_paid_coins", "price_paid_diamonds", "purchased_at")
    search_fields = ("profile__user__username", "shop_item__name")
    autocomplete_fields = ("profile", "shop_item")
