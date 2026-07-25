import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_userprofile_last_seen"),
        ("competition", "0002_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(name="leaderboard", unique_together=set()),
        migrations.RemoveField(model_name="leaderboard", name="department"),
        migrations.RemoveField(model_name="leaderboard", name="profile"),
        migrations.RemoveField(model_name="leaderboard", name="season"),
        migrations.DeleteModel(name="Leaderboard"),
        migrations.CreateModel(
            name="ScoreEvent",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("amount", models.PositiveIntegerField()),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="score_events",
                        to="accounts.userprofile",
                    ),
                ),
            ],
            options={
                "verbose_name": "Evenement de score",
                "verbose_name_plural": "Evenements de score",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="scoreevent",
            index=models.Index(fields=["profile", "created_at"], name="competition_profile_759e88_idx"),
        ),
        migrations.CreateModel(
            name="PeriodWinner",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "scope",
                    models.CharField(
                        choices=[("national", "National"), ("friends", "Amis")], default="national", max_length=12
                    ),
                ),
                (
                    "period",
                    models.CharField(
                        choices=[
                            ("weekly", "Hebdomadaire"),
                            ("monthly", "Mensuel"),
                            ("yearly", "Annuel"),
                        ],
                        max_length=10,
                    ),
                ),
                ("period_key", models.CharField(help_text="Ex: 2026-W30, 2026-07, 2026", max_length=16)),
                ("score", models.PositiveIntegerField()),
                ("coins_awarded", models.PositiveIntegerField(default=0)),
                ("diamonds_awarded", models.PositiveIntegerField(default=0)),
                ("granted_at", models.DateTimeField(auto_now_add=True)),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="period_wins",
                        to="accounts.userprofile",
                    ),
                ),
            ],
            options={
                "verbose_name": "Vainqueur de periode",
                "verbose_name_plural": "Vainqueurs de periode",
                "ordering": ["-granted_at"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="periodwinner",
            unique_together={("scope", "period", "period_key")},
        ),
    ]
