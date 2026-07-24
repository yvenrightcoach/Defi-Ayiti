"""
Reglages pour la suite de tests automatises (pytest-django).

Objectif : zero dependance externe (pas de Supabase, pas de Redis) pour que
les tests tournent partout, y compris en CI, sans configuration prealable.
"""
from .base import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Hachage de mot de passe rapide : les tests n'ont pas besoin de securite reelle.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

GUEST_MODE_ENABLED = True

# Le stockage manifeste (whitenoise/S3) exige un manifest genere par
# `collectstatic`, absent en test. Le tableau de bord admin rend un vrai
# template Django (contrairement au reste de l'API, en JSON) et a donc
# besoin que {% static %} se resolve sans manifest ici.
STORAGES = {**STORAGES, "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}}
