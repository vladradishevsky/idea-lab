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
