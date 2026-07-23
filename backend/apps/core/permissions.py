"""Permissions objet partagees entre les apps de jeu."""
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsSelf(BasePermission):
    """Autorise uniquement le proprietaire d'un objet UserProfile."""

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


class IsProfileOwner(BasePermission):
    """Autorise uniquement le proprietaire d'un objet possedant un champ 'profile'."""

    def has_object_permission(self, request, view, obj):
        return obj.profile.user_id == request.user.id


class ReadOnlyOrProfileOwner(BasePermission):
    """Lecture libre (authentifiee) ; ecriture reservee au proprietaire (champ 'profile')."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.profile.user_id == request.user.id
