from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, RefreshView, LogoutViewSet, UserViewSet, whoami

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"logout", LogoutViewSet, basename="logout")

urlpatterns = [
    path("whoami/", whoami, name="whoami"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("", include(router.urls)),
]
