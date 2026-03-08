from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ideas", "0002_stage"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="stage",
            constraint=models.UniqueConstraint(
                fields=("source_system", "source_id"),
                name="ideas_stage_source_system_source_id_uniq",
            ),
        ),
        migrations.AddConstraint(
            model_name="stage",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(seo_kd_percent__isnull=True)
                    | models.Q(seo_kd_percent__gte=0, seo_kd_percent__lte=100)
                ),
                name="ideas_stage_seo_kd_percent_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="stage",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(implementation_ease_percent__isnull=True)
                    | models.Q(
                        implementation_ease_percent__gte=0,
                        implementation_ease_percent__lte=100,
                    )
                ),
                name="ideas_stage_implementation_ease_percent_range",
            ),
        ),
        migrations.AddIndex(
            model_name="stage",
            index=models.Index(fields=["status"], name="ideas_stage_status_idx"),
        ),
        migrations.AddIndex(
            model_name="stage",
            index=models.Index(fields=["created_at"], name="ideas_stage_created_at_idx"),
        ),
        migrations.AddIndex(
            model_name="stage",
            index=models.Index(fields=["is_filled"], name="ideas_stage_is_filled_idx"),
        ),
        migrations.AddIndex(
            model_name="stage",
            index=models.Index(
                fields=["status", "created_at"],
                name="ideas_stage_st_cr_idx",
            ),
        ),
    ]
