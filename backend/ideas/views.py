from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ideas.serializers import StageIngestionSerializer


class StageIngestionView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        is_many = isinstance(request.data, list)
        payload = request.data if is_many else [request.data]
        serializer = StageIngestionSerializer(data=payload, many=True)
        serializer.is_valid(raise_exception=True)
        created_count = 0
        ignored_count = 0

        for item in serializer.validated_data:
            stage = StageIngestionSerializer.Meta.model.objects.filter(
                source_system=item["source_system"],
                source_id=item["source_id"],
            ).first()

            if stage is not None:
                ignored_count += 1
                continue

            StageIngestionSerializer.Meta.model.objects.create(**item)
            created_count += 1

        return Response(
            {
                "created": created_count,
                "ignored": ignored_count,
            },
            status=status.HTTP_201_CREATED if created_count > 0 else status.HTTP_200_OK,
        )
