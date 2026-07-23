import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("defi_ayiti")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Tâches périodiques (quêtes quotidiennes, reset des séries, fin de saison, etc.)
app.conf.beat_schedule = {
    "reset-daily-missions": {
        "task": "apps.rewards.tasks.reset_daily_missions",
        "schedule": crontab(hour=0, minute=0),
    },
    "compute-weekly-leaderboard": {
        "task": "apps.competition.tasks.compute_weekly_leaderboard",
        "schedule": crontab(hour=0, minute=5, day_of_week="monday"),
    },
    "check-season-status": {
        "task": "apps.competition.tasks.check_season_status",
        "schedule": crontab(hour=1, minute=0),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Requête de débogage : {self.request!r}")
