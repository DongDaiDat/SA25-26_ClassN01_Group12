import pytest
from modules.course_catalog.infrastructure.models import Course
from modules.course_catalog.application.services import CoursePrereqService

@pytest.mark.django_db
def test_prereq_cycle_detected():
    a = Course.objects.create(code="A", name="A", credits=3)
    b = Course.objects.create(code="B", name="B", credits=3)
    CoursePrereqService.set_prerequisites(str(a.id), [str(b.id)])
    with pytest.raises(Exception):
        CoursePrereqService.set_prerequisites(str(b.id), [str(a.id)])
