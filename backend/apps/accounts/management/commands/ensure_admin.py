"""
Cree le compte super admin s'il n'existe pas encore, a partir de variables
d'environnement. Concu pour tourner a chaque deploiement (build command),
car le plan gratuit de Render n'offre pas d'acces Shell pour lancer
`createsuperuser` a la main. Ne fait rien si les variables sont absentes ou
si le compte existe deja (idempotent, ne touche jamais un mot de passe
existant).
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Cree le compte super admin depuis ADMIN_USERNAME/ADMIN_EMAIL/ADMIN_PASSWORD si absent."

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME")
        email = os.environ.get("ADMIN_EMAIL")
        password = os.environ.get("ADMIN_PASSWORD")

        if not (username and email and password):
            self.stdout.write("ADMIN_USERNAME/ADMIN_EMAIL/ADMIN_PASSWORD absents : super admin ignore.")
            return

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Super admin '{username}' deja present, aucune action.")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Super admin '{username}' cree."))
