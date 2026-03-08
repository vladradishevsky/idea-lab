from django.contrib import admin

from ideas.models import SourceSystem, Stage


@admin.register(SourceSystem)
class SourceSystemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "base_url", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("name", "base_url")
    ordering = ("name",)


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "source_system",
        "source_id",
        "status",
        "is_filled",
        "category",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "is_filled", "source_system", "category", "created_at", "updated_at")
    search_fields = ("title", "source_id", "source_url", "description", "custom_title")
    autocomplete_fields = ("source_system",)
    ordering = ("created_at",)
    list_select_related = ("source_system",)
