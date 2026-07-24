from django.db import migrations

PACKS = [
    {"name": "Petit sac", "diamonds_amount": 100, "price_usd_cents": 299, "order": 1},
    {"name": "Sac moyen", "diamonds_amount": 350, "price_usd_cents": 799, "order": 2},
    {"name": "Grand coffre", "diamonds_amount": 1000, "price_usd_cents": 1999, "order": 3},
]


def seed_packs(apps, schema_editor):
    DiamondPack = apps.get_model("payments", "DiamondPack")
    for data in PACKS:
        DiamondPack.objects.get_or_create(name=data["name"], defaults=data)


def remove_packs(apps, schema_editor):
    DiamondPack = apps.get_model("payments", "DiamondPack")
    DiamondPack.objects.filter(name__in=[p["name"] for p in PACKS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_packs, remove_packs),
    ]
