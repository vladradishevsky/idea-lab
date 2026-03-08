from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ideas", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Stage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_id", models.CharField(max_length=512)),
                ("source_url", models.TextField()),
                ("title", models.TextField()),
                ("description", models.TextField(blank=True, null=True)),
                ("category", models.TextField(blank=True, null=True)),
                ("custom_title", models.TextField(blank=True, null=True)),
                ("custom_description", models.TextField(blank=True, null=True)),
                ("existing_solution", models.TextField(blank=True, null=True)),
                ("original_revenue_estimate", models.TextField(blank=True, null=True)),
                ("seo_query", models.TextField(blank=True, null=True)),
                ("seo_kd_percent", models.IntegerField(blank=True, null=True)),
                ("seo_popularity_vs_adblocker", models.TextField(blank=True, null=True)),
                ("planned_feature", models.TextField(blank=True, null=True)),
                ("implementation_ease_percent", models.IntegerField(blank=True, null=True)),
                ("risks", models.TextField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "New"),
                            ("accepted", "Accepted"),
                            ("rejected", "Rejected"),
                            ("in_progress", "In progress"),
                            ("completed", "Completed"),
                        ],
                        default="new",
                        max_length=20,
                    ),
                ),
                ("is_filled", models.BooleanField(default=False)),
                ("filled_at", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "source_system",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="stages",
                        to="ideas.sourcesystem",
                    ),
                ),
            ],
        ),
    ]
