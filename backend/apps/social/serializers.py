"""Serializers DRF de l'app 'social'."""
from rest_framework import serializers

from apps.accounts.models import UserProfile
from apps.accounts.serializers import UserProfileSerializer

from .models import Friend


class FriendSerializer(serializers.ModelSerializer):
    requester = UserProfileSerializer(read_only=True)
    addressee = UserProfileSerializer(read_only=True)

    class Meta:
        model = Friend
        fields = ("id", "requester", "addressee", "status", "created_at", "responded_at")
        read_only_fields = ("id", "requester", "addressee", "status", "created_at", "responded_at")


class CreateFriendRequestSerializer(serializers.Serializer):
    addressee_id = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all())
