import logging

from django.db.models import Count, Q
from rest_framework import exceptions, status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from ideas.models import SourceSystem, Stage, StageStatus
from ideas.serializers import (
    SourceSystemSerializer,
    StageElaborationUpdateSerializer,
    StageDetailSerializer,
    StageIngestionSerializer,
    StageListFilterSerializer,
    StageListSerializer,
    StageStatusUpdateSerializer,
)


logger = logging.getLogger("ideas.ingest")

ELABORATION_FIELDS = tuple(StageElaborationUpdateSerializer.Meta.fields)


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


class SourceSystemListView(ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = SourceSystemSerializer
    queryset = SourceSystem.objects.filter(is_active=True).order_by("name", "id")
    pagination_class = None


class StageDashboardAggregatesView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        aggregates = Stage.objects.aggregate(
            new=Count("id", filter=Q(status=StageStatus.NEW)),
            accepted=Count("id", filter=Q(status=StageStatus.ACCEPTED)),
            rejected=Count("id", filter=Q(status=StageStatus.REJECTED)),
            in_progress=Count("id", filter=Q(status=StageStatus.IN_PROGRESS)),
            completed=Count("id", filter=Q(status=StageStatus.COMPLETED)),
        )

        return Response(aggregates)


class StageDetailView(RetrieveAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = StageDetailSerializer
    queryset = Stage.objects.select_related("source_system")


class StageStatusUpdateView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, pk):
        serializer = StageStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stage = Stage.objects.select_related("source_system").filter(pk=pk).first()
        if stage is None:
            raise exceptions.NotFound()

        if stage.status != StageStatus.NEW:
            raise exceptions.ValidationError(
                {"status": ["Quick status update is only available for stages in 'new' status."]}
            )

        stage.status = serializer.validated_data["status"]
        stage.save(update_fields=["status", "updated_at"])

        return Response(StageDetailSerializer(stage).data, status=status.HTTP_200_OK)


class StageElaborationUpdateView(APIView):
    authentication_classes = []
    permission_classes = []

    def patch(self, request, pk):
        stage = Stage.objects.select_related("source_system").filter(pk=pk).first()
        if stage is None:
            raise exceptions.NotFound()

        allowed_fields = set(StageElaborationUpdateSerializer.Meta.fields)
        unexpected_fields = sorted(set(request.data.keys()) - allowed_fields)
        if unexpected_fields:
            raise exceptions.ValidationError(
                {field: ["This field is not allowed."] for field in unexpected_fields}
            )

        serializer = StageElaborationUpdateSerializer(
            stage,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        stage.refresh_from_db()

        if stage.is_filled:
            if stage.filled_at is None:
                stage.filled_at = timezone.localdate()
            stage.status = StageStatus.COMPLETED
            stage.save(update_fields=["status", "filled_at", "updated_at"])
            stage.refresh_from_db()
        elif any(
            getattr(stage, field) not in (None, "") for field in ELABORATION_FIELDS
        ):
            stage.status = StageStatus.IN_PROGRESS
            stage.save(update_fields=["status", "updated_at"])
            stage.refresh_from_db()

        return Response(StageDetailSerializer(stage).data, status=status.HTTP_200_OK)
