import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("heroes", "0001_initial"),
        ("accounts", "0005_userprofile_last_seen"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="avatar_hero",
            field=models.ForeignKey(
                blank=True,
                help_text="Heros debloque choisi comme photo de profil (remplace avatar_url a l'affichage)",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="heroes.hero",
            ),
        ),
    ]
