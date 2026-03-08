from django.urls import path

from config.views import ApiRootView, HealthCheckView
from ideas.views import StageIngestionView, StageListView


app_name = "api"


urlpatterns = [
    path("", ApiRootView.as_view(), name="root"),
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("ingest/", StageIngestionView.as_view(), name="ingest"),
    path("stages/", StageListView.as_view(), name="stage-list"),
]
