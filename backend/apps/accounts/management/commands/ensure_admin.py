"""
Cree ou resynchronise le compte super admin a partir de variables
d'environnement. Concu pour tourner a chaque deploiement (build command),
car le plan gratuit de Render n'offre pas d'acces Shell pour lancer
`createsuperuser`/`changepassword` a la main. Le mot de passe et l'email
sont resynchronises a chaque run : si les variables d'environnement
changent sur Render, le compte suit -- pas besoin de supprimer l'ancien
compte pour corriger un mot de passe errone.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Cree/resynchronise le compte super admin depuis ADMIN_USERNAME/ADMIN_EMAIL/ADMIN_PASSWORD."

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME")
        email = os.environ.get("ADMIN_EMAIL")
        password = os.environ.get("ADMIN_PASSWORD")

        if not (username and email and password):
            self.stdout.write("ADMIN_USERNAME/ADMIN_EMAIL/ADMIN_PASSWORD absents : super admin ignore.")
            return

        User = get_user_model()
        admin, created = User.objects.get_or_create(
            username=username, defaults={"email": email, "is_staff": True, "is_superuser": True}
        )
        admin.email = email
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password(password)
        admin.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Super admin '{username}' cree."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Super admin '{username}' resynchronise."))
