from django.core.exceptions import ValidationError
from django.apps import apps
from django.db import IntegrityError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

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

    def test_post_ingestion_endpoint_accepts_batch_payload(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork Batch API",
            base_url="https://kwork.ru",
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="project-batch-duplicate",
            source_url="https://kwork.ru/projects/existing",
            title="Existing project",
        )
        payload = [
            {
                "source_system": source_system.pk,
                "source_id": "project-batch-1",
                "source_url": "https://kwork.ru/projects/project-batch-1",
                "title": "Batch project 1",
                "description": "First new record",
                "category": "development",
            },
            {
                "source_system": source_system.pk,
                "source_id": "project-batch-duplicate",
                "source_url": "https://kwork.ru/projects/should-be-ignored",
                "title": "Duplicate project",
            },
            {
                "source_system": source_system.pk,
                "source_id": "project-batch-2",
                "source_url": "https://kwork.ru/projects/project-batch-2",
                "title": "Batch project 2",
            },
        ]

        response = self.client.post(
            reverse("api:ingest"),
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"created": 2, "ignored": 1})
        self.assertEqual(Stage.objects.count(), 3)
        self.assertTrue(
            Stage.objects.filter(
                source_system=source_system,
                source_id="project-batch-1",
                status=StageStatus.NEW,
            ).exists()
        )
        self.assertTrue(
            Stage.objects.filter(
                source_system=source_system,
                source_id="project-batch-2",
                status=StageStatus.NEW,
            ).exists()
        )

        duplicate_stage = Stage.objects.get(source_id="project-batch-duplicate")

        self.assertEqual(duplicate_stage.source_url, "https://kwork.ru/projects/existing")
        self.assertEqual(duplicate_stage.title, "Existing project")

    def test_post_ingestion_endpoint_logs_created_and_ignored_counts(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork Logging API",
            base_url="https://kwork.ru",
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="project-log-duplicate",
            source_url="https://kwork.ru/projects/existing-log",
            title="Existing log project",
        )
        payload = [
            {
                "source_system": source_system.pk,
                "source_id": "project-log-1",
                "source_url": "https://kwork.ru/projects/project-log-1",
                "title": "Log project 1",
            },
            {
                "source_system": source_system.pk,
                "source_id": "project-log-duplicate",
                "source_url": "https://kwork.ru/projects/ignored-log",
                "title": "Ignored log project",
            },
        ]

        with self.assertLogs("ideas.ingest", level="INFO") as captured_logs:
            response = self.client.post(
                reverse("api:ingest"),
                data=payload,
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 201)
        self.assertIn(
            "ingest completed items=2 created=1 ignored=1",
            captured_logs.output[0],
        )

    def test_post_ingestion_endpoint_logs_validation_errors(self) -> None:
        with self.assertLogs("ideas.ingest", level="WARNING") as captured_logs:
            response = self.client.post(
                reverse("api:ingest"),
                data=[{"description": "missing required fields"}],
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn("ingest validation_failed items=1", captured_logs.output[0])
        self.assertIn("source_system", captured_logs.output[0])
        self.assertIn("source_id", captured_logs.output[0])
        self.assertIn("source_url", captured_logs.output[0])
        self.assertIn("title", captured_logs.output[0])


class StageListApiTests(TestCase):
    def test_stage_list_endpoint_returns_paginated_response(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork List API",
            base_url="https://kwork.ru",
        )

        for index in range(21):
            Stage.objects.create(
                source_system=source_system,
                source_id=f"project-list-{index}",
                source_url=f"https://kwork.ru/projects/{index}",
                title=f"Project {index}",
            )

        response = self.client.get(reverse("api:stage-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 21)
        self.assertIsNotNone(response.json()["next"])
        self.assertIsNone(response.json()["previous"])
        self.assertEqual(len(response.json()["results"]), 20)

    def test_stage_list_endpoint_orders_by_created_at_ascending(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork Ordered List API",
            base_url="https://kwork.ru",
        )
        newest_stage = Stage.objects.create(
            source_system=source_system,
            source_id="project-order-newest",
            source_url="https://kwork.ru/projects/newest",
            title="Newest project",
        )
        oldest_stage = Stage.objects.create(
            source_system=source_system,
            source_id="project-order-oldest",
            source_url="https://kwork.ru/projects/oldest",
            title="Oldest project",
        )
        middle_stage = Stage.objects.create(
            source_system=source_system,
            source_id="project-order-middle",
            source_url="https://kwork.ru/projects/middle",
            title="Middle project",
        )

        now = timezone.now()
        Stage.objects.filter(pk=oldest_stage.pk).update(created_at=now - timezone.timedelta(days=2))
        Stage.objects.filter(pk=middle_stage.pk).update(created_at=now - timezone.timedelta(days=1))
        Stage.objects.filter(pk=newest_stage.pk).update(created_at=now)

        response = self.client.get(reverse("api:stage-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["source_id"] for item in response.json()["results"]],
            [
                "project-order-oldest",
                "project-order-middle",
                "project-order-newest",
            ],
        )

    def test_stage_list_endpoint_hides_rejected_by_default(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork Hidden Rejected API",
            base_url="https://kwork.ru",
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="project-visible",
            source_url="https://kwork.ru/projects/visible",
            title="Visible project",
            status=StageStatus.NEW,
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="project-rejected",
            source_url="https://kwork.ru/projects/rejected",
            title="Rejected project",
            status=StageStatus.REJECTED,
        )

        response = self.client.get(reverse("api:stage-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            [item["source_id"] for item in response.json()["results"]],
            ["project-visible"],
        )

    def test_stage_list_endpoint_filters_by_status(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork Status Filter API",
            base_url="https://kwork.ru",
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="project-accepted",
            source_url="https://kwork.ru/projects/accepted",
            title="Accepted project",
            status=StageStatus.ACCEPTED,
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="project-rejected",
            source_url="https://kwork.ru/projects/rejected",
            title="Rejected project",
            status=StageStatus.REJECTED,
        )

        response = self.client.get(
            reverse("api:stage-list"),
            data={"status": StageStatus.REJECTED},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            [item["source_id"] for item in response.json()["results"]],
            ["project-rejected"],
        )

    def test_stage_list_endpoint_filters_by_source_system_id(self) -> None:
        source_system_one = SourceSystem.objects.create(
            name="Kwork Source Filter API",
            base_url="https://kwork.ru",
        )
        source_system_two = SourceSystem.objects.create(
            name="FL Source Filter API",
            base_url="https://fl.ru",
        )
        Stage.objects.create(
            source_system=source_system_one,
            source_id="project-source-1",
            source_url="https://kwork.ru/projects/source-1",
            title="Source project 1",
        )
        Stage.objects.create(
            source_system=source_system_two,
            source_id="project-source-2",
            source_url="https://fl.ru/projects/source-2",
            title="Source project 2",
        )

        response = self.client.get(
            reverse("api:stage-list"),
            data={"source_system_id": source_system_two.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            [item["source_id"] for item in response.json()["results"]],
            ["project-source-2"],
        )

    def test_stage_list_endpoint_filters_by_category(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork Category Filter API",
            base_url="https://kwork.ru",
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="project-category-dev",
            source_url="https://kwork.ru/projects/category-dev",
            title="Development project",
            category="development",
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="project-category-design",
            source_url="https://kwork.ru/projects/category-design",
            title="Design project",
            category="design",
        )

        response = self.client.get(
            reverse("api:stage-list"),
            data={"category": "design"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            [item["source_id"] for item in response.json()["results"]],
            ["project-category-design"],
        )

    def test_stage_list_endpoint_filters_by_is_filled(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork Filled Filter API",
            base_url="https://kwork.ru",
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="project-filled-false",
            source_url="https://kwork.ru/projects/filled-false",
            title="Not filled project",
            is_filled=False,
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="project-filled-true",
            source_url="https://kwork.ru/projects/filled-true",
            title="Filled project",
            is_filled=True,
        )

        response = self.client.get(
            reverse("api:stage-list"),
            data={"is_filled": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            [item["source_id"] for item in response.json()["results"]],
            ["project-filled-true"],
        )

    def test_stage_list_endpoint_includes_rejected_when_requested(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork Include Rejected API",
            base_url="https://kwork.ru",
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="project-new",
            source_url="https://kwork.ru/projects/new",
            title="New project",
            status=StageStatus.NEW,
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="project-rejected",
            source_url="https://kwork.ru/projects/rejected",
            title="Rejected project",
            status=StageStatus.REJECTED,
        )

        response = self.client.get(
            reverse("api:stage-list"),
            data={"include_rejected": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)
        self.assertEqual(
            [item["source_id"] for item in response.json()["results"]],
            ["project-new", "project-rejected"],
        )

    def test_stage_list_endpoint_combines_filters(self) -> None:
        source_system_one = SourceSystem.objects.create(
            name="Kwork Combined Filter API",
            base_url="https://kwork.ru",
        )
        source_system_two = SourceSystem.objects.create(
            name="FL Combined Filter API",
            base_url="https://fl.ru",
        )
        Stage.objects.create(
            source_system=source_system_one,
            source_id="project-combined-match",
            source_url="https://kwork.ru/projects/combined-match",
            title="Matching project",
            category="development",
            status=StageStatus.ACCEPTED,
            is_filled=True,
        )
        Stage.objects.create(
            source_system=source_system_one,
            source_id="project-combined-wrong-category",
            source_url="https://kwork.ru/projects/combined-wrong-category",
            title="Wrong category project",
            category="design",
            status=StageStatus.ACCEPTED,
            is_filled=True,
        )
        Stage.objects.create(
            source_system=source_system_two,
            source_id="project-combined-wrong-source",
            source_url="https://fl.ru/projects/combined-wrong-source",
            title="Wrong source project",
            category="development",
            status=StageStatus.ACCEPTED,
            is_filled=True,
        )
        Stage.objects.create(
            source_system=source_system_one,
            source_id="project-combined-wrong-filled",
            source_url="https://kwork.ru/projects/combined-wrong-filled",
            title="Wrong filled project",
            category="development",
            status=StageStatus.ACCEPTED,
            is_filled=False,
        )

        response = self.client.get(
            reverse("api:stage-list"),
            data={
                "status": StageStatus.ACCEPTED,
                "source_system_id": source_system_one.pk,
                "category": "development",
                "is_filled": "true",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            [item["source_id"] for item in response.json()["results"]],
            ["project-combined-match"],
        )


class StageDetailApiTests(TestCase):
    def test_stage_detail_endpoint_returns_full_stage_card(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork Detail API",
            base_url="https://kwork.ru",
        )
        stage = Stage.objects.create(
            source_system=source_system,
            source_id="project-detail-1",
            source_url="https://kwork.ru/projects/detail-1",
            title="Detailed project",
            description="Detailed description",
            category="development",
            custom_title="Custom project title",
            custom_description="Custom project description",
            existing_solution="Spreadsheet plus manual work",
            original_revenue_estimate="$500 MRR",
            seo_query="idea validation software",
            seo_kd_percent=42,
            seo_popularity_vs_adblocker="Lower than adblocker, but steady",
            planned_feature="Competitor snapshot",
            implementation_ease_percent=67,
            risks="Low search intent conversion",
            status=StageStatus.ACCEPTED,
            is_filled=True,
            filled_at=timezone.localdate(),
        )

        response = self.client.get(
            reverse("api:stage-detail", kwargs={"pk": stage.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "id": stage.pk,
                "source_system_id": source_system.pk,
                "source_id": "project-detail-1",
                "source_url": "https://kwork.ru/projects/detail-1",
                "title": "Detailed project",
                "description": "Detailed description",
                "category": "development",
                "custom_title": "Custom project title",
                "custom_description": "Custom project description",
                "existing_solution": "Spreadsheet plus manual work",
                "original_revenue_estimate": "$500 MRR",
                "seo_query": "idea validation software",
                "seo_kd_percent": 42,
                "seo_popularity_vs_adblocker": "Lower than adblocker, but steady",
                "planned_feature": "Competitor snapshot",
                "implementation_ease_percent": 67,
                "risks": "Low search intent conversion",
                "status": StageStatus.ACCEPTED,
                "is_filled": True,
                "filled_at": stage.filled_at.isoformat(),
                "created_at": stage.created_at.isoformat().replace("+00:00", "Z"),
                "updated_at": stage.updated_at.isoformat().replace("+00:00", "Z"),
            },
        )


class StageStatusUpdateApiTests(TestCase):
    def test_stage_status_update_endpoint_accepts_new_stage(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork Status Update API",
            base_url="https://kwork.ru",
        )
        stage = Stage.objects.create(
            source_system=source_system,
            source_id="project-status-accepted",
            source_url="https://kwork.ru/projects/status-accepted",
            title="Accepted via quick filter",
            status=StageStatus.NEW,
        )

        response = self.client.post(
            reverse("api:stage-status-update", kwargs={"pk": stage.pk}),
            data={"status": StageStatus.ACCEPTED},
            content_type="application/json",
        )

        stage.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(stage.status, StageStatus.ACCEPTED)
        self.assertEqual(response.json()["id"], stage.pk)
        self.assertEqual(response.json()["status"], StageStatus.ACCEPTED)

    def test_stage_status_update_endpoint_rejects_new_stage(self) -> None:
        source_system = SourceSystem.objects.create(
            name="FL Status Update API",
            base_url="https://fl.ru",
        )
        stage = Stage.objects.create(
            source_system=source_system,
            source_id="project-status-rejected",
            source_url="https://fl.ru/projects/status-rejected",
            title="Rejected via quick filter",
            status=StageStatus.NEW,
        )

        response = self.client.post(
            reverse("api:stage-status-update", kwargs={"pk": stage.pk}),
            data={"status": StageStatus.REJECTED},
            content_type="application/json",
        )

        stage.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(stage.status, StageStatus.REJECTED)
        self.assertEqual(response.json()["status"], StageStatus.REJECTED)

    def test_stage_status_update_endpoint_rejects_invalid_transition(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork Invalid Transition API",
            base_url="https://kwork.ru",
        )
        stage = Stage.objects.create(
            source_system=source_system,
            source_id="project-status-invalid",
            source_url="https://kwork.ru/projects/status-invalid",
            title="Invalid quick filter transition",
            status=StageStatus.ACCEPTED,
        )

        response = self.client.post(
            reverse("api:stage-status-update", kwargs={"pk": stage.pk}),
            data={"status": StageStatus.REJECTED},
            content_type="application/json",
        )

        stage.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(stage.status, StageStatus.ACCEPTED)
        self.assertEqual(
            response.json(),
            {
                "status": [
                    "Quick status update is only available for stages in 'new' status."
                ]
            },
        )


class StageElaborationUpdateApiTests(TestCase):
    def test_stage_elaboration_update_endpoint_saves_elaboration_fields(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Kwork Elaboration API",
            base_url="https://kwork.ru",
        )
        stage = Stage.objects.create(
            source_system=source_system,
            source_id="project-elaboration-1",
            source_url="https://kwork.ru/projects/elaboration-1",
            title="Elaboration target",
            status=StageStatus.ACCEPTED,
        )

        response = self.client.patch(
            reverse("api:stage-elaboration-update", kwargs={"pk": stage.pk}),
            data={
                "custom_title": "Validated niche title",
                "custom_description": "Expanded market summary",
                "seo_query": "b2b lead scoring tool",
                "seo_kd_percent": 34,
                "planned_feature": "Landing page generator",
                "implementation_ease_percent": 71,
                "risks": "Demand may be narrow",
            },
            content_type="application/json",
        )

        stage.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(stage.custom_title, "Validated niche title")
        self.assertEqual(stage.custom_description, "Expanded market summary")
        self.assertEqual(stage.seo_query, "b2b lead scoring tool")
        self.assertEqual(stage.seo_kd_percent, 34)
        self.assertEqual(stage.planned_feature, "Landing page generator")
        self.assertEqual(stage.implementation_ease_percent, 71)
        self.assertEqual(stage.risks, "Demand may be narrow")
        self.assertEqual(stage.status, StageStatus.IN_PROGRESS)
        self.assertFalse(stage.is_filled)
        self.assertEqual(response.json()["custom_title"], "Validated niche title")
        self.assertEqual(response.json()["status"], StageStatus.IN_PROGRESS)

    def test_stage_elaboration_update_endpoint_moves_new_stage_to_in_progress(self) -> None:
        source_system = SourceSystem.objects.create(
            name="New To In Progress API",
            base_url="https://example.com",
        )
        stage = Stage.objects.create(
            source_system=source_system,
            source_id="project-elaboration-new",
            source_url="https://example.com/projects/elaboration-new",
            title="New elaboration target",
            status=StageStatus.NEW,
        )

        response = self.client.patch(
            reverse("api:stage-elaboration-update", kwargs={"pk": stage.pk}),
            data={"existing_solution": "Manual analyst workflow"},
            content_type="application/json",
        )

        stage.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(stage.existing_solution, "Manual analyst workflow")
        self.assertEqual(stage.status, StageStatus.IN_PROGRESS)
        self.assertFalse(stage.is_filled)
        self.assertEqual(response.json()["status"], StageStatus.IN_PROGRESS)

    def test_stage_elaboration_update_endpoint_keeps_completed_flag_out_of_scope(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Filled Elaboration API",
            base_url="https://example.com",
        )
        stage = Stage.objects.create(
            source_system=source_system,
            source_id="project-elaboration-filled",
            source_url="https://example.com/projects/elaboration-filled",
            title="Filled elaboration target",
            status=StageStatus.ACCEPTED,
            is_filled=True,
        )

        response = self.client.patch(
            reverse("api:stage-elaboration-update", kwargs={"pk": stage.pk}),
            data={"custom_title": "Already filled project"},
            content_type="application/json",
        )

        stage.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(stage.custom_title, "Already filled project")
        self.assertEqual(stage.status, StageStatus.COMPLETED)
        self.assertTrue(stage.is_filled)
        self.assertIsNotNone(stage.filled_at)
        self.assertEqual(response.json()["status"], StageStatus.COMPLETED)

    def test_stage_elaboration_update_endpoint_sets_completed_and_filled_at(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Complete Elaboration API",
            base_url="https://example.com",
        )
        stage = Stage.objects.create(
            source_system=source_system,
            source_id="project-elaboration-complete",
            source_url="https://example.com/projects/elaboration-complete",
            title="Completion target",
            status=StageStatus.IN_PROGRESS,
            is_filled=False,
            custom_title="Ready for completion",
        )

        response = self.client.patch(
            reverse("api:stage-elaboration-update", kwargs={"pk": stage.pk}),
            data={"is_filled": True},
            content_type="application/json",
        )

        stage.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(stage.is_filled)
        self.assertEqual(stage.status, StageStatus.COMPLETED)
        self.assertEqual(stage.filled_at, timezone.localdate())
        self.assertEqual(response.json()["status"], StageStatus.COMPLETED)
        self.assertEqual(response.json()["filled_at"], stage.filled_at.isoformat())

    def test_stage_elaboration_update_endpoint_preserves_existing_filled_at(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Preserve FilledAt API",
            base_url="https://example.com",
        )
        original_filled_at = timezone.localdate() - timezone.timedelta(days=3)
        stage = Stage.objects.create(
            source_system=source_system,
            source_id="project-elaboration-preserve-filled-at",
            source_url="https://example.com/projects/elaboration-preserve-filled-at",
            title="Preserve filled at target",
            status=StageStatus.COMPLETED,
            is_filled=True,
            filled_at=original_filled_at,
        )

        response = self.client.patch(
            reverse("api:stage-elaboration-update", kwargs={"pk": stage.pk}),
            data={"custom_description": "Refined after completion"},
            content_type="application/json",
        )

        stage.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(stage.status, StageStatus.COMPLETED)
        self.assertTrue(stage.is_filled)
        self.assertEqual(stage.filled_at, original_filled_at)
        self.assertEqual(response.json()["filled_at"], original_filled_at.isoformat())

    def test_stage_elaboration_update_endpoint_rejects_service_fields(self) -> None:
        source_system = SourceSystem.objects.create(
            name="FL Elaboration API",
            base_url="https://fl.ru",
        )
        stage = Stage.objects.create(
            source_system=source_system,
            source_id="project-elaboration-2",
            source_url="https://fl.ru/projects/elaboration-2",
            title="Elaboration invalid payload target",
            status=StageStatus.ACCEPTED,
        )

        response = self.client.patch(
            reverse("api:stage-elaboration-update", kwargs={"pk": stage.pk}),
            data={
                "custom_title": "Legit update",
                "status": StageStatus.COMPLETED,
                "filled_at": timezone.localdate().isoformat(),
            },
            content_type="application/json",
        )

        stage.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertIsNone(stage.custom_title)
        self.assertEqual(stage.status, StageStatus.ACCEPTED)
        self.assertFalse(stage.is_filled)
        self.assertIsNone(stage.filled_at)
        self.assertEqual(
            response.json(),
            {
                "status": ["This field is not allowed."],
                "filled_at": ["This field is not allowed."],
            },
        )


class StageDashboardAggregatesApiTests(TestCase):
    def test_dashboard_aggregates_endpoint_returns_counts_by_status(self) -> None:
        source_system = SourceSystem.objects.create(
            name="Dashboard Aggregates API",
            base_url="https://example.com",
        )

        Stage.objects.create(
            source_system=source_system,
            source_id="dashboard-new",
            source_url="https://example.com/dashboard-new",
            title="New dashboard project",
            status=StageStatus.NEW,
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="dashboard-accepted",
            source_url="https://example.com/dashboard-accepted",
            title="Accepted dashboard project",
            status=StageStatus.ACCEPTED,
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="dashboard-rejected",
            source_url="https://example.com/dashboard-rejected",
            title="Rejected dashboard project",
            status=StageStatus.REJECTED,
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="dashboard-in-progress-1",
            source_url="https://example.com/dashboard-in-progress-1",
            title="In progress dashboard project 1",
            status=StageStatus.IN_PROGRESS,
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="dashboard-in-progress-2",
            source_url="https://example.com/dashboard-in-progress-2",
            title="In progress dashboard project 2",
            status=StageStatus.IN_PROGRESS,
        )
        Stage.objects.create(
            source_system=source_system,
            source_id="dashboard-completed",
            source_url="https://example.com/dashboard-completed",
            title="Completed dashboard project",
            status=StageStatus.COMPLETED,
            is_filled=True,
            filled_at=timezone.localdate(),
        )

        response = self.client.get(reverse("api:dashboard-aggregates"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "new": 1,
                "accepted": 1,
                "rejected": 1,
                "in_progress": 2,
                "completed": 1,
            },
        )
