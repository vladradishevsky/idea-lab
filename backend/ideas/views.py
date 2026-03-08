import logging

from rest_framework import exceptions, status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from ideas.models import Stage
from ideas.serializers import StageIngestionSerializer, StageListSerializer


logger = logging.getLogger("ideas.ingest")


class StagePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class StageIngestionView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        is_many = isinstance(request.data, list)
        payload = request.data if is_many else [request.data]
        serializer = StageIngestionSerializer(data=payload, many=True)

        try:
            serializer.is_valid(raise_exception=True)
        except exceptions.ValidationError:
            logger.warning(
                "ingest validation_failed items=%s errors=%s",
                len(payload),
                serializer.errors,
            )
            raise

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

        logger.info(
            "ingest completed items=%s created=%s ignored=%s",
            len(payload),
            created_count,
            ignored_count,
        )

        return Response(
            {
                "created": created_count,
                "ignored": ignored_count,
            },
            status=status.HTTP_201_CREATED if created_count > 0 else status.HTTP_200_OK,
        )


class StageListView(ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = StageListSerializer
    pagination_class = StagePagination
    queryset = Stage.objects.select_related("source_system").order_by("created_at", "id")
