from rest_framework.routers import DefaultRouter
from .views import NotificationMessageViewSet, ManualSendViewSet

router = DefaultRouter()
router.register(r"messages", NotificationMessageViewSet, basename="messages")
router.register(r"send", ManualSendViewSet, basename="send")

urlpatterns = router.urls
