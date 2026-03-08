from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.apps import apps
from django.test import SimpleTestCase, TestCase

from ideas.models import SourceSystem, Stage, StageStatus


class IdeasAppConfigTests(SimpleTestCase):
    def test_ideas_app_is_installed(self) -> None:
        app_config = apps.get_app_config("ideas")

        self.assertEqual(app_config.name, "ideas")


class SourceSystemModelTests(TestCase):
    def test_source_system_can_be_created_and_read(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork",
            base_url="https://kwork.ru",
            is_active=True,
        )

        loaded_source_system = SourceSystem.objects.get(pk=source_system.pk)

        self.assertEqual(loaded_source_system.name, "Kwork")
        self.assertEqual(loaded_source_system.base_url, "https://kwork.ru")
        self.assertTrue(loaded_source_system.is_active)
        self.assertIsNotNone(loaded_source_system.created_at)
        self.assertIsNotNone(loaded_source_system.updated_at)


class StageModelTests(TestCase):
    def test_stage_uses_new_status_by_default(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork",
            base_url="https://kwork.ru",
        )

        stage = Stage.objects.create(
            source_system=source_system,
            source_id="project-123",
            source_url="https://kwork.ru/projects/123",
            title="Build an MVP",
        )

        self.assertEqual(stage.status, StageStatus.NEW)
        self.assertFalse(stage.is_filled)
        self.assertIsNone(stage.filled_at)

    def test_stage_source_system_and_source_id_pair_must_be_unique(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork",
            base_url="https://kwork.ru",
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="project-123",
            source_url="https://kwork.ru/projects/123",
            title="Build an MVP",
        )

        with self.assertRaises(IntegrityError):
            Stage.objects.create(
                source_system=source_system,
                source_id="project-123",
                source_url="https://kwork.ru/projects/123-duplicate",
                title="Duplicate project",
            )

    def test_stage_rejects_percent_values_outside_allowed_range(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork",
            base_url="https://kwork.ru",
        )
        stage = Stage(
            source_system=source_system,
            source_id="project-124",
            source_url="https://kwork.ru/projects/124",
            title="Validate metrics",
            seo_kd_percent=101,
            implementation_ease_percent=-1,
        )

        with self.assertRaises(ValidationError) as error:
            stage.full_clean()

        self.assertIn("seo_kd_percent", error.exception.message_dict)
        self.assertIn("implementation_ease_percent", error.exception.message_dict)
