from rest_framework.routers import DefaultRouter
from .views import TermViewSet

router = DefaultRouter()
router.register(r"terms", TermViewSet, basename="terms")

urlpatterns = router.urls
