from rest_framework.routers import DefaultRouter
from .views import ProgramViewSet, CurriculumVersionViewSet, CurriculumNodeViewSet, CurriculumRuleViewSet

router = DefaultRouter()
router.register(r"programs", ProgramViewSet, basename="programs")
router.register(r"curricula", CurriculumVersionViewSet, basename="curricula")
router.register(r"nodes", CurriculumNodeViewSet, basename="curriculum-nodes")
router.register(r"rules", CurriculumRuleViewSet, basename="curriculum-rules")

urlpatterns = router.urls
