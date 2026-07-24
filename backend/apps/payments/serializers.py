"""Serializers DRF de l'app 'payments'."""
from rest_framework import serializers

from .models import DiamondPack, DiamondPurchase


class DiamondPackSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiamondPack
        fields = ("id", "name", "diamonds_amount", "price_usd_cents", "order")


class CreateCheckoutSerializer(serializers.Serializer):
    pack_id = serializers.UUIDField()


class CheckoutSessionSerializer(serializers.Serializer):
    checkout_url = serializers.URLField()


class DiamondPurchaseSerializer(serializers.ModelSerializer):
    pack = DiamondPackSerializer(read_only=True)

    class Meta:
        model = DiamondPurchase
        fields = ("id", "pack", "provider", "status", "created_at")
        read_only_fields = fields
