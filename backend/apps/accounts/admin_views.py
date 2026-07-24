"""Tableau de bord du compte super admin : joueurs, revenus, activite, economie."""
from datetime import timedelta

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Q, Sum
from django.shortcuts import render
from django.utils import timezone

from apps.geography.models import Department
from apps.payments.models import DiamondPurchase, PaymentStatus
from apps.progress.models import PlayerProgress

from .models import User, UserProfile

ONLINE_WINDOW_MINUTES = 5


def _revenue_cents(queryset) -> int:
    return queryset.aggregate(total=Sum("pack__price_usd_cents"))["total"] or 0


@staff_member_required
@user_passes_test(lambda user: user.is_superuser)
def dashboard_view(request):
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    online_since = now - timedelta(minutes=ONLINE_WINDOW_MINUTES)

    total_users = User.objects.count()
    guest_users = User.objects.filter(is_guest=True).count()
    new_today = User.objects.filter(date_joined__date=today).count()
    new_this_week = User.objects.filter(date_joined__gte=week_ago).count()

    online_qs = UserProfile.objects.select_related("user").filter(last_seen__gte=online_since)

    paid = DiamondPurchase.objects.filter(status=PaymentStatus.PAID).select_related("pack")
    revenue = {
        "today": _revenue_cents(paid.filter(created_at__date=today)) / 100,
        "week": _revenue_cents(paid.filter(created_at__gte=week_ago)) / 100,
        "month": _revenue_cents(paid.filter(created_at__gte=month_ago)) / 100,
        "total": _revenue_cents(paid) / 100,
    }

    top_spenders = list(
        paid.values("profile_id", "profile__user__username")
        .annotate(total_cents=Sum("pack__price_usd_cents"), purchase_count=Count("id"))
        .order_by("-total_cents")[:10]
    )
    for row in top_spenders:
        row["total_usd"] = row["total_cents"] / 100

    economy = UserProfile.objects.aggregate(total_coins=Sum("coins"), total_diamonds=Sum("diamonds"))

    department_completion = list(
        Department.objects.annotate(
            completions=Count(
                "progress_entries", filter=Q(progress_entries__is_completed=True), distinct=True
            )
        )
        .order_by("order")
        .values("name", "order", "completions")
    )

    context = {
        **admin.site.each_context(request),
        "title": "Tableau de bord",
        "total_users": total_users,
        "guest_users": guest_users,
        "registered_users": total_users - guest_users,
        "new_today": new_today,
        "new_this_week": new_this_week,
        "online_count": online_qs.count(),
        "online_users": online_qs.order_by("-last_seen")[:20],
        "revenue": revenue,
        "top_spenders": top_spenders,
        "top_trophies": UserProfile.objects.select_related("user").order_by("-trophies")[:10],
        "top_xp": UserProfile.objects.select_related("user").order_by("-xp")[:10],
        "top_streak": UserProfile.objects.select_related("user").order_by("-best_win_streak")[:10],
        "economy": economy,
        "department_completion": department_completion,
        "active_stakes": PlayerProgress.objects.filter(pending_stake__gt=0).count(),
    }
    return render(request, "admin/dashboard.html", context)
