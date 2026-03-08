from rest_framework import serializers

from ideas.models import Stage


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
