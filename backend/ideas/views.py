import logging

from rest_framework import exceptions, status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from ideas.models import Stage, StageStatus
from ideas.serializers import (
    StageIngestionSerializer,
    StageListFilterSerializer,
    StageListSerializer,
)


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

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = StageListFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)

        statuses = filters.validated_data.get("status")
        source_system_id = filters.validated_data.get("source_system_id")
        category = filters.validated_data.get("category")
        is_filled = filters.validated_data.get("is_filled")
        include_rejected = filters.validated_data.get("include_rejected", False)

        if statuses:
            queryset = queryset.filter(status__in=statuses)
        elif not include_rejected:
            queryset = queryset.exclude(status=StageStatus.REJECTED)

        if source_system_id is not None:
            queryset = queryset.filter(source_system_id=source_system_id)

        if category is not None:
            queryset = queryset.filter(category=category)

        if is_filled is not None:
            queryset = queryset.filter(is_filled=is_filled)

        return queryset
