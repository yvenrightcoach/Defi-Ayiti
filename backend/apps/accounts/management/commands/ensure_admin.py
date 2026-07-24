"""
Cree ou resynchronise LE compte super admin (un seul, celui declare par les
variables d'environnement) a partir de ADMIN_USERNAME/ADMIN_EMAIL/
ADMIN_PASSWORD. Concu pour tourner a chaque deploiement (build command), car
le plan gratuit de Render n'offre pas d'acces Shell pour lancer
`createsuperuser`/`changepassword` a la main.

Comportement :
- Le mot de passe et l'email sont resynchronises a chaque run : changer les
  variables sur Render suffit, pas besoin de supprimer un compte a la main.
- Tout AUTRE compte superutilisateur (cree lors d'un essai precedent, par
  exemple sous un nom mal saisi) est supprime a chaque run : il n'existe
  jamais qu'un seul compte super admin, celui qui correspond aux variables
  actuelles.
- Ne doit JAMAIS faire echouer le build : une erreur ici ne doit pas
  empecher le reste de l'application de se deployer. Toute exception est
  attrapee et seulement loguee.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Cree/resynchronise LE compte super admin depuis ADMIN_USERNAME/ADMIN_EMAIL/ADMIN_PASSWORD."

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME")
        email = os.environ.get("ADMIN_EMAIL")
        password = os.environ.get("ADMIN_PASSWORD")

        if not (username and email and password):
            self.stdout.write("ADMIN_USERNAME/ADMIN_EMAIL/ADMIN_PASSWORD absents : super admin ignore.")
            return

        try:
            self._sync_admin(username, email, password)
        except Exception as exc:  # noqa: BLE001 - ne doit jamais bloquer le build
            self.stderr.write(self.style.ERROR(f"ensure_admin a echoue (build non bloque) : {exc!r}"))

    def _sync_admin(self, username, email, password):
        User = get_user_model()

        # Un seul admin bootstrap a la fois : tout autre superutilisateur
        # (cree lors d'un essai precedent, ex. mauvaise casse) est supprime.
        deleted, _ = User.objects.filter(is_superuser=True).exclude(username=username).delete()
        if deleted:
            self.stdout.write(f"{deleted} ancien(s) compte(s) super admin supprime(s).")

        # Email est unique : liberere celui d'un compte non-superadmin qui le
        # detiendrait deja (evite un IntegrityError qui ferait echouer tout).
        for stale in User.objects.filter(email=email).exclude(username=username):
            stale.email = f"stale-admin-{stale.pk}@invalid.local"
            stale.save(update_fields=["email"])

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
