from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework.permissions import AllowAny

from modules.shared.views import health

urlpatterns = [
    path("admin/", admin.site.urls),

    # Health
    path("api/health", health, name="health"),
    path("api/health/", health, name="health_slash"),


    # OpenAPI schema + docs (AllowAny để schema generation không bị crash bởi RBAC/AnonymousUser)
    path(
        "api/schema/",
        SpectacularAPIView.as_view(permission_classes=[AllowAny]),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema", permission_classes=[AllowAny]),
        name="docs",
    ),
    # Optional: Redoc (có thể bỏ nếu không cần)
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema", permission_classes=[AllowAny]),
        name="redoc",
    ),

    # API v1
    path("api/v1/auth/", include("modules.identity_access.presentation.urls")),
    path("api/v1/audit/", include("modules.audit.presentation.urls")),
    path("api/v1/program/", include("modules.program.presentation.urls")),
    path("api/v1/course-catalog/", include("modules.course_catalog.presentation.urls")),
    path("api/v1/term/", include("modules.term_scheduling.presentation.urls")),
    path("api/v1/section/", include("modules.class_section.presentation.urls")),
    path("api/v1/enrollment/", include("modules.enrollment.presentation.urls")),
    path("api/v1/assessment/", include("modules.assessment.presentation.urls")),
    path("api/v1/certificate/", include("modules.certificate.presentation.urls")),
]
