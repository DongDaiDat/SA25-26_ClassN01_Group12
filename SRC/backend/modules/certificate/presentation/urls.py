from rest_framework.routers import DefaultRouter
from .views import CertificateDefinitionViewSet, CertificateIssueViewSet

router = DefaultRouter()
router.register(r"definitions", CertificateDefinitionViewSet, basename="cert-definitions")
router.register(r"issues", CertificateIssueViewSet, basename="cert-issues")

urlpatterns = router.urls
