from django.test import SimpleTestCase
from django.urls import reverse


class ApiRootTests(SimpleTestCase):
    def test_api_root_returns_available_endpoints(self) -> None:
        response = self.client.get(reverse("api:root"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "health": "http://testserver/api/health/",
                "ingest": "http://testserver/api/ingest/",
            },
        )


class HealthCheckTests(SimpleTestCase):
    def test_health_endpoint_returns_ready_payload(self) -> None:
        response = self.client.get(reverse("api:health-check"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
