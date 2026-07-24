from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def healthz(request):
    """Verification de sante pour Render (et tout autre orchestrateur)."""
    return JsonResponse({"status": "ok"})

api_v1_patterns = [
    path("auth/", include("apps.accounts.urls")),
    path("heroes/", include("apps.heroes.urls")),
    path("geography/", include("apps.geography.urls")),
    path("quiz/", include("apps.quiz.urls")),
    path("progress/", include("apps.progress.urls")),
    path("battles/", include("apps.battles.urls")),
    path("social/", include("apps.social.urls")),
    path("competition/", include("apps.competition.urls")),
    path("rewards/", include("apps.rewards.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("payments/", include("apps.payments.urls")),
]

urlpatterns = [
    path("healthz/", healthz, name="healthz"),
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1_patterns)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=getattr(settings, "MEDIA_ROOT", None))
