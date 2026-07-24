"""Serializers DRF de l'app 'geography'."""
from rest_framework import serializers

from .models import Department, Level


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = (
            "id", "department", "order", "name", "description", "question_count",
            "required_score", "xp_reward", "coin_reward", "is_boss_level", "unlocks_hero",
        )


class DepartmentSerializer(serializers.ModelSerializer):
    """Departement, avec 'is_unlocked' calcule pour le joueur connecte."""

    is_unlocked = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = (
            "id", "name", "slug", "code", "capital", "description",
            "map_image", "icon", "boss_name", "order", "is_unlocked",
        )

    def get_is_unlocked(self, obj) -> bool:
        """Le premier departement est toujours ouvert ; les suivants exigent
        d'avoir termine (boss vaincu) le departement precedent."""
        if obj.order <= 1:
            return True

        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False

        # Import tardif pour eviter un cycle d'imports entre 'geography' et 'progress'.
        from apps.progress.models import PlayerProgress

        return PlayerProgress.objects.filter(
            profile__user=request.user,
            department__order=obj.order - 1,
            is_completed=True,
        ).exists()


class DepartmentDetailSerializer(DepartmentSerializer):
    """Departement avec la liste de ses chapitres (utilise sur /geography/departments/{id}/)."""

    levels = LevelSerializer(many=True, read_only=True)

    class Meta(DepartmentSerializer.Meta):
        fields = DepartmentSerializer.Meta.fields + ("levels",)
