"""Fonctions utilitaires partagees de l'app 'social' (reutilisees hors de cette app, ex: classements)."""
from django.db.models import Q

from .models import Friend, FriendStatus


def get_accepted_friend_ids(profile) -> list:
    """Identifiants des profils amis confirmes de `profile` (sans `profile` lui-meme)."""
    if profile is None:
        return []
    accepted = Friend.objects.filter(
        Q(requester=profile) | Q(addressee=profile), status=FriendStatus.ACCEPTED
    ).values_list("requester_id", "addressee_id")
    return [addressee_id if requester_id == profile.id else requester_id for requester_id, addressee_id in accepted]
