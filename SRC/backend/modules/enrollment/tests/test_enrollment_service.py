import pytest
from django.utils import timezone
from datetime import timedelta, date, time

from django.contrib.auth import get_user_model
from modules.course_catalog.infrastructure.models import Course
from modules.term_scheduling.infrastructure.models import Term
from modules.class_section.infrastructure.models import Section, ScheduleSlot
from modules.enrollment.application.services import EnrollmentService

User = get_user_model()

@pytest.mark.django_db
def test_enroll_success_no_overquota():
    student = User.objects.create_user(username="s1", password="x", role=User.ROLE_STUDENT)
    c = Course.objects.create(code="C101", name="Course 101", credits=3)
    now = timezone.now()
    t = Term.objects.create(
        code="T1", name="Term 1",
        start_date=date.today(), end_date=date.today(),
        enroll_open_at=now - timedelta(hours=1),
        enroll_close_at=now + timedelta(hours=1),
        status=Term.STATUS_OPEN,
    )
    sec = Section.objects.create(term_id=t.id, course_id=c.id, section_code="A", capacity=1)
    ScheduleSlot.objects.create(section=sec, day_of_week=1, start_time=time(9,0), end_time=time(10,0))
    res = EnrollmentService.enroll(student=student, section_id=str(sec.id), idempotency_key="k1", correlation_id="c1")
    assert res["status"] == "ACTIVE"
    # second seat should fail due to quota
    student2 = User.objects.create_user(username="s2", password="x", role=User.ROLE_STUDENT)
    with pytest.raises(Exception):
        EnrollmentService.enroll(student=student2, section_id=str(sec.id), idempotency_key="k2", correlation_id="c2")
