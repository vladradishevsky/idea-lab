from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class ApiRootView(APIView):
    def get(self, request):
        return Response(
            {
                "health": reverse("api:health-check", request=request),
                "ingest": reverse("api:ingest", request=request),
                "stages": reverse("api:stage-list", request=request),
                "stage_detail": reverse("api:stage-detail", kwargs={"pk": 1}, request=request),
                "stage_status_update": reverse(
                    "api:stage-status-update", kwargs={"pk": 1}, request=request
                ),
            }
        )


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok"})
