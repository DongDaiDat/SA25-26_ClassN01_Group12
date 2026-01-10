from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("ms/notification/health", include("notification.urls_health")),
    path("ms/notification/schema", SpectacularAPIView.as_view(), name="schema"),
    path("ms/notification/docs", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("ms/notification/", include("notification.urls")),
]
