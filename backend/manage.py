#!/usr/bin/env python
"""Utilitaire en ligne de commande de Django pour Défi Ayiti."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossible d'importer Django. Vérifiez que votre environnement "
            "virtuel est activé et que les dépendances sont installées."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
