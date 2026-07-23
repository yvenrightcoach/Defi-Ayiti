"""Vues DRF de l'app 'geography'."""
from rest_framework import viewsets

from .models import Department, Level
from .serializers import DepartmentDetailSerializer, DepartmentSerializer, LevelSerializer


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """Catalogue des 10 departements du mode Aventure (lecture seule)."""

    queryset = Department.objects.prefetch_related("levels").all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DepartmentDetailSerializer
        return DepartmentSerializer


class LevelViewSet(viewsets.ReadOnlyModelViewSet):
    """Catalogue des chapitres d'aventure, filtrable par departement (?department=<id>)."""

    serializer_class = LevelSerializer
    filterset_fields = ["department", "is_boss_level"]
    queryset = Level.objects.select_related("department").all()
