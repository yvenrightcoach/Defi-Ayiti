"""Suivi de presence en ligne des joueurs (utilise par le tableau de bord admin)."""
from django.utils import timezone

LAST_SEEN_UPDATE_INTERVAL_SECONDS = 60


class TrackLastSeenMiddleware:
    """
    Met a jour UserProfile.last_seen sur les requetes authentifiees. Limite
    l'ecriture a une fois par minute par joueur pour eviter de solliciter la
    base de donnees sur chaque requete.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            profile = getattr(user, "profile", None)
            if profile is not None:
                now = timezone.now()
                stale = (
                    profile.last_seen is None
                    or (now - profile.last_seen).total_seconds() > LAST_SEEN_UPDATE_INTERVAL_SECONDS
                )
                if stale:
                    profile.last_seen = now
                    profile.save(update_fields=["last_seen"])

        return response
