from django.urls import path

from config.views import ApiRootView, HealthCheckView
from ideas.views import (
    SourceSystemListView,
    StageDashboardAggregatesView,
    StageElaborationUpdateView,
    StageDetailView,
    StageIngestionView,
    StageListView,
    StageStatusUpdateView,
)


app_name = "api"


urlpatterns = [
    path("", ApiRootView.as_view(), name="root"),
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("source-systems/", SourceSystemListView.as_view(), name="source-system-list"),
    path("dashboard/aggregates/", StageDashboardAggregatesView.as_view(), name="dashboard-aggregates"),
    path("ingest/", StageIngestionView.as_view(), name="ingest"),
    path("stages/", StageListView.as_view(), name="stage-list"),
    path("stages/<int:pk>/", StageDetailView.as_view(), name="stage-detail"),
    path(
        "stages/<int:pk>/elaboration/",
        StageElaborationUpdateView.as_view(),
        name="stage-elaboration-update",
    ),
    path("stages/<int:pk>/status/", StageStatusUpdateView.as_view(), name="stage-status-update"),
]
