from django.db import migrations


INITIAL_SOURCE_SYSTEMS = [
    {
        "name": "Kwork",
        "base_url": "https://kwork.ru/projects",
        "is_active": True,
    },
    {
        "name": "Freelance.ru",
        "base_url": "https://freelance.ru/project/search?q=&a=0&a=1&v=0&v=1&c=&c%5B%5D=116&c%5B%5D=724&c%5B%5D=4",
        "is_active": True,
    },
    {
        "name": "FL.ru",
        "base_url": "https://www.fl.ru/projects/category/programmirovanie//",
        "is_active": True,
    },
]


def seed_source_systems(apps, schema_editor):
    source_system_model = apps.get_model("ideas", "SourceSystem")

    for source_system in INITIAL_SOURCE_SYSTEMS:
        source_system_model.objects.update_or_create(
            name=source_system["name"],
            defaults={
                "base_url": source_system["base_url"],
                "is_active": source_system["is_active"],
            },
        )


def unseed_source_systems(apps, schema_editor):
    source_system_model = apps.get_model("ideas", "SourceSystem")
    source_system_model.objects.filter(
        name__in=[source_system["name"] for source_system in INITIAL_SOURCE_SYSTEMS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("ideas", "0003_stage_constraints"),
    ]

    operations = [
        migrations.RunPython(seed_source_systems, unseed_source_systems),
    ]
