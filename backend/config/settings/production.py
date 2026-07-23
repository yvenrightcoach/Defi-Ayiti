import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

# Suivi d'erreurs (optionnel) : n'active Sentry que si un DSN est fourni.
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Render place le service derrière un proxy ; le nom d'hôte externe est
# fourni via la variable d'environnement RENDER_EXTERNAL_HOSTNAME.
render_hostname = env("RENDER_EXTERNAL_HOSTNAME", default=None)
if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)  # noqa: F405
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_hostname}")  # noqa: F405

# Sans fournisseur SMTP configure (EMAIL_HOST vide), utiliser le backend
# reel ferait planter chaque inscription/reinitialisation de mot de passe
# (tentative de connexion a un hote vide). On bascule sur un backend "dummy"
# qui ignore silencieusement les emails tant qu'un service (SendGrid,
# Mailgun...) n'est pas branche.
EMAIL_HOST = env("EMAIL_HOST", default="")
if EMAIL_HOST:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_PORT = env.int("EMAIL_PORT", default=587)
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
else:
    EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
