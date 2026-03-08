from django.core.exceptions import ValidationError
from django.apps import apps
from django.db import IntegrityError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from ideas.models import SourceSystem, Stage, StageStatus
from ideas.serializers import StageIngestionSerializer


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

    def test_initial_source_systems_are_seeded(self) -> None:
        expected_sources = {
            "Kwork": "https://kwork.ru/projects",
            "Freelance.ru": "https://freelance.ru/project/search?q=&a=0&a=1&v=0&v=1&c=&c%5B%5D=116&c%5B%5D=724&c%5B%5D=4",
            "FL.ru": "https://www.fl.ru/projects/category/programmirovanie//",
        }

        actual_sources = dict(
            SourceSystem.objects.filter(name__in=expected_sources)
            .values_list("name", "base_url")
        )

        self.assertEqual(actual_sources, expected_sources)


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


class StageIngestionSerializerTests(TestCase):
    def test_serializer_accepts_valid_ingestion_payload(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork",
            base_url="https://kwork.ru",
        )
        payload = {
            "source_system": source_system.pk,
            "source_id": "project-999",
            "source_url": "https://kwork.ru/projects/999",
            "title": "Launch a SaaS MVP",
            "description": "Need a product team for a quick launch",
            "category": "development",
        }

        serializer = StageIngestionSerializer(data=payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["source_system"], source_system)
        self.assertEqual(serializer.validated_data["source_id"], payload["source_id"])
        self.assertEqual(serializer.validated_data["source_url"], payload["source_url"])
        self.assertEqual(serializer.validated_data["title"], payload["title"])
        self.assertEqual(serializer.validated_data["description"], payload["description"])
        self.assertEqual(serializer.validated_data["category"], payload["category"])

    def test_serializer_requires_mandatory_ingestion_fields(self) -> None:
        serializer = StageIngestionSerializer(
            data={
                "description": "Payload without required fields",
                "category": "development",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            set(serializer.errors.keys()),
            {"source_system", "source_id", "source_url", "title"},
        )


class StageIngestionApiTests(TestCase):
    def test_post_ingestion_endpoint_creates_stage_with_new_status(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork API",
            base_url="https://kwork.ru",
        )
        payload = {
            "source_system": source_system.pk,
            "source_id": "project-api-1",
            "source_url": "https://kwork.ru/projects/project-api-1",
            "title": "API ingestion test",
            "description": "Created via ingestion endpoint",
            "category": "development",
        }

        response = self.client.post(
            reverse("api:ingest"),
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Stage.objects.count(), 1)

        stage = Stage.objects.get()

        self.assertEqual(stage.source_system, source_system)
        self.assertEqual(stage.source_id, payload["source_id"])
        self.assertEqual(stage.source_url, payload["source_url"])
        self.assertEqual(stage.title, payload["title"])
        self.assertEqual(stage.description, payload["description"])
        self.assertEqual(stage.category, payload["category"])
        self.assertEqual(stage.status, StageStatus.NEW)
        self.assertEqual(
            response.json(),
            {
                "created": 1,
                "ignored": 0,
            },
        )

    def test_post_ingestion_endpoint_ignores_duplicate_without_updating_stage(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork Duplicate API",
            base_url="https://kwork.ru",
        )
        original_stage = Stage.objects.create(
            source_system=source_system,
            source_id="project-duplicate-1",
            source_url="https://kwork.ru/projects/original",
            title="Original title",
            description="Original description",
            category="original-category",
        )
        payload = {
            "source_system": source_system.pk,
            "source_id": original_stage.source_id,
            "source_url": "https://kwork.ru/projects/updated",
            "title": "Updated title",
            "description": "Updated description",
            "category": "updated-category",
        }

        response = self.client.post(
            reverse("api:ingest"),
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"created": 0, "ignored": 1})
        self.assertEqual(Stage.objects.count(), 1)

        original_stage.refresh_from_db()

        self.assertEqual(original_stage.source_url, "https://kwork.ru/projects/original")
        self.assertEqual(original_stage.title, "Original title")
        self.assertEqual(original_stage.description, "Original description")
        self.assertEqual(original_stage.category, "original-category")
        self.assertEqual(original_stage.status, StageStatus.NEW)
