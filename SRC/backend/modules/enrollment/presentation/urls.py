from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import EnrollmentViewSet

router = DefaultRouter()
router.register(r"enrollments", EnrollmentViewSet, basename="enrollments")

urlpatterns = router.urls
