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
        validated_data = serializer.validated_data
        stage = StageIngestionSerializer.Meta.model.objects.filter(
            source_system=validated_data["source_system"],
            source_id=validated_data["source_id"],
        ).first()

        if stage is not None:
            return Response(
                {
                    "created": 0,
                    "ignored": 1,
                },
                status=status.HTTP_200_OK,
            )

        serializer.save()

        return Response(
            {
                "created": 1,
                "ignored": 0,
            },
            status=status.HTTP_201_CREATED,
        )
