from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ideas.serializers import StageIngestionSerializer


class StageIngestionView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = StageIngestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stage = serializer.save()

        return Response(
            {
                "id": stage.pk,
                "status": stage.status,
            },
            status=status.HTTP_201_CREATED,
        )
