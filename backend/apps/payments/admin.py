from django.contrib import admin

from .models import DiamondPack, DiamondPurchase


@admin.register(DiamondPack)
class DiamondPackAdmin(admin.ModelAdmin):
    list_display = ("name", "diamonds_amount", "price_usd_cents", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(DiamondPurchase)
class DiamondPurchaseAdmin(admin.ModelAdmin):
    list_display = ("profile", "pack", "provider", "status", "diamonds_credited", "created_at")
    list_filter = ("provider", "status", "diamonds_credited")
    search_fields = ("profile__user__username", "provider_reference")
    autocomplete_fields = ("profile", "pack")
