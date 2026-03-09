from rest_framework import serializers

from ideas.models import SourceSystem, Stage, StageStatus


class SourceSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceSystem
        fields = [
            "id",
            "name",
            "base_url",
            "is_active",
        ]


class StageIngestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        validators = []
        fields = [
            "source_system",
            "source_id",
            "source_url",
            "title",
            "description",
            "category",
        ]
        extra_kwargs = {
            "source_system": {"required": True},
            "source_id": {"required": True},
            "source_url": {"required": True},
            "title": {"required": True},
            "description": {"required": False, "allow_null": True, "allow_blank": True},
            "category": {"required": False, "allow_null": True, "allow_blank": True},
        }


class StageListSerializer(serializers.ModelSerializer):
    source_system_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Stage
        fields = [
            "id",
            "source_system_id",
            "source_id",
            "source_url",
            "title",
            "description",
            "category",
            "status",
            "is_filled",
            "filled_at",
            "created_at",
            "updated_at",
        ]


class StageDetailSerializer(serializers.ModelSerializer):
    source_system_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Stage
        fields = [
            "id",
            "source_system_id",
            "source_id",
            "source_url",
            "title",
            "description",
            "category",
            "custom_title",
            "custom_description",
            "existing_solution",
            "original_revenue_estimate",
            "seo_query",
            "seo_kd_percent",
            "seo_popularity_vs_adblocker",
            "planned_feature",
            "implementation_ease_percent",
            "risks",
            "status",
            "is_filled",
            "filled_at",
            "created_at",
            "updated_at",
        ]


class StageListFilterSerializer(serializers.Serializer):
    status = serializers.CharField(required=False)
    source_system_id = serializers.IntegerField(required=False, min_value=1)
    category = serializers.CharField(required=False)
    is_filled = serializers.BooleanField(required=False)
    include_rejected = serializers.BooleanField(required=False, default=False)

    def validate_status(self, value):
        statuses = [item.strip() for item in value.split(",") if item.strip()]
        valid_statuses = {choice for choice, _ in StageStatus.choices}
        invalid_statuses = [status for status in statuses if status not in valid_statuses]

        if not statuses:
            raise serializers.ValidationError("At least one status must be provided.")

        if invalid_statuses:
            raise serializers.ValidationError(
                f"Unsupported status values: {', '.join(invalid_statuses)}"
            )

        return statuses


class StageStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            (StageStatus.ACCEPTED, "Accepted"),
            (StageStatus.REJECTED, "Rejected"),
        ]
    )


class StageElaborationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = [
            "custom_title",
            "custom_description",
            "existing_solution",
            "original_revenue_estimate",
            "seo_query",
            "seo_kd_percent",
            "seo_popularity_vs_adblocker",
            "planned_feature",
            "implementation_ease_percent",
            "risks",
            "is_filled",
        ]
