"""Vues DRF de l'app 'social'."""
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.accounts.models import UserProfile
from apps.accounts.serializers import UserProfileSerializer

from .models import Friend, FriendStatus
from .serializers import CreateFriendRequestSerializer, FriendSerializer
from .services import get_accepted_friend_ids


class FriendViewSet(viewsets.ModelViewSet):
    """Demandes d'ami : envoi, acceptation, refus et liste des amis."""

    http_method_names = ["get", "post", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateFriendRequestSerializer
        return FriendSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Friend.objects.none()
        profile = UserProfile.objects.filter(user=self.request.user).first()
        return (
            Friend.objects.filter(Q(requester=profile) | Q(addressee=profile))
            .select_related("requester__user", "addressee__user")
        )

    def create(self, request, *args, **kwargs):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        payload = CreateFriendRequestSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        addressee = payload.validated_data["addressee_id"]

        if addressee.id == profile.id:
            raise ValidationError("Impossible de s'ajouter soi-meme comme ami.")

        friend, created = Friend.objects.get_or_create(
            requester=profile, addressee=addressee, defaults={"status": FriendStatus.PENDING}
        )
        if not created:
            raise ValidationError("Une demande existe deja entre ces deux joueurs.")
        return Response(FriendSerializer(friend).data, status=201)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        friend = self._get_pending_as_addressee(request)
        friend.status = FriendStatus.ACCEPTED
        friend.responded_at = timezone.now()
        friend.save(update_fields=["status", "responded_at"])
        return Response(FriendSerializer(friend).data)

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        friend = self._get_pending_as_addressee(request)
        friend.status = FriendStatus.DECLINED
        friend.responded_at = timezone.now()
        friend.save(update_fields=["status", "responded_at"])
        return Response(FriendSerializer(friend).data)

    def _get_pending_as_addressee(self, request) -> Friend:
        friend = self.get_object()
        profile = UserProfile.objects.filter(user=request.user).first()
        if friend.addressee_id != profile.id:
            raise PermissionDenied("Seul le destinataire peut repondre a cette demande.")
        if friend.status != FriendStatus.PENDING:
            raise ValidationError("Cette demande a deja recu une reponse.")
        return friend

    @action(detail=False, methods=["get"])
    def friends(self, request):
        """Liste des amis confirmes (l'autre profil de chaque amitie acceptee)."""
        profile = UserProfile.objects.filter(user=request.user).first()
        friend_ids = get_accepted_friend_ids(profile)
        friend_profiles = UserProfile.objects.filter(id__in=friend_ids).select_related("user")
        return Response(UserProfileSerializer(friend_profiles, many=True).data)
