# unimis/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from pathlib import Path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("miscore.urls")),   # toàn bộ UI & API ở app miscore
]

# Dev: serve static từ miscore/static
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=(Path(settings.BASE_DIR) / "miscore" / "static")
    )
