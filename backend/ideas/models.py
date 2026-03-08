from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class SourceSystem(models.Model):
    name = models.CharField(max_length=255)
    base_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class StageStatus(models.TextChoices):
    NEW = "new", "New"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    IN_PROGRESS = "in_progress", "In progress"
    COMPLETED = "completed", "Completed"


class Stage(models.Model):
    source_system = models.ForeignKey(
        SourceSystem,
        on_delete=models.CASCADE,
        related_name="stages",
    )
    source_id = models.CharField(max_length=512)
    source_url = models.TextField()
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    category = models.TextField(null=True, blank=True)

    custom_title = models.TextField(null=True, blank=True)
    custom_description = models.TextField(null=True, blank=True)
    existing_solution = models.TextField(null=True, blank=True)
    original_revenue_estimate = models.TextField(null=True, blank=True)
    seo_query = models.TextField(null=True, blank=True)
    seo_kd_percent = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    seo_popularity_vs_adblocker = models.TextField(null=True, blank=True)
    planned_feature = models.TextField(null=True, blank=True)
    implementation_ease_percent = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    risks = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=StageStatus.choices,
        default=StageStatus.NEW,
    )
    is_filled = models.BooleanField(default=False)
    filled_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source_system", "source_id"],
                name="ideas_stage_source_system_source_id_uniq",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(seo_kd_percent__isnull=True)
                    | models.Q(seo_kd_percent__gte=0, seo_kd_percent__lte=100)
                ),
                name="ideas_stage_seo_kd_percent_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(implementation_ease_percent__isnull=True)
                    | models.Q(
                        implementation_ease_percent__gte=0,
                        implementation_ease_percent__lte=100,
                    )
                ),
                name="ideas_stage_implementation_ease_percent_range",
            ),
        ]
        indexes = [
            models.Index(fields=["status"], name="ideas_stage_status_idx"),
            models.Index(fields=["created_at"], name="ideas_stage_created_at_idx"),
            models.Index(fields=["is_filled"], name="ideas_stage_is_filled_idx"),
            models.Index(
                fields=["status", "created_at"],
                name="ideas_stage_st_cr_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.title
