from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, SectionViewSet, ScheduleSlotViewSet

router = DefaultRouter()
router.register(r"rooms", RoomViewSet, basename="rooms")
router.register(r"sections", SectionViewSet, basename="sections")
router.register(r"slots", ScheduleSlotViewSet, basename="slots")

urlpatterns = router.urls
