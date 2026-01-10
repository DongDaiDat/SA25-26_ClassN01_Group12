import uuid
from datetime import time

import pytest
from django.utils import timezone

from modules.class_section.infrastructure.models import Section, ScheduleSlot
from modules.assessment.infrastructure.models import GradeRecord
from modules.enrollment.application.services import EnrollmentService
from modules.enrollment.infrastructure.models import Enrollment
from modules.shared.exceptions import BusinessRuleViolation, ConflictError

pytestmark = pytest.mark.django_db


def test_enroll_fails_when_prereq_not_met(users, section_basic):
    student = users["student1"]
    idem = "idem-" + str(uuid.uuid4())
    with pytest.raises(BusinessRuleViolation) as e:
        EnrollmentService.enroll(student=student, section_id=str(section_basic.id), idempotency_key=idem, correlation_id="test")
    assert e.value.code == "PREREQ_NOT_MET"


def test_enroll_succeeds_when_prereq_met(users, section_basic, course_graph):
    student = users["student1"]
    # create published passing grade for prereq course C101
    GradeRecord.objects.create(
        student=student,
        section_id=uuid.uuid4(),
        term_id=section_basic.term_id,
        course_id=course_graph["C101"].id,
        grade_value=7.0,
        status=GradeRecord.STATUS_PUBLISHED,
        updated_by=student,
    )
    idem = "idem-" + str(uuid.uuid4())
    res = EnrollmentService.enroll(student=student, section_id=str(section_basic.id), idempotency_key=idem, correlation_id="test")
    assert res["status"] == Enrollment.STATUS_ACTIVE


def test_enroll_fails_on_schedule_conflict(users, section_basic, course_graph, term_open):
    student = users["student1"]
    # pass prereq
    GradeRecord.objects.create(
        student=student,
        section_id=uuid.uuid4(),
        term_id=section_basic.term_id,
        course_id=course_graph["C101"].id,
        grade_value=7.0,
        status=GradeRecord.STATUS_PUBLISHED,
        updated_by=student,
    )

    # create another section in same term with overlapping slot
    other = Section.objects.create(
        term_id=term_open.id,
        course_id=course_graph["C101"].id,
        section_code="S2",
        capacity=10,
        enrolled_count=0,
        status="ACTIVE",
    )
    ScheduleSlot.objects.create(section=other, day_of_week=1, start_time=time(9, 30), end_time=time(10, 30), room=None)

    # enroll into other first (no prereq there)
    idem1 = "idem-" + str(uuid.uuid4())
    EnrollmentService.enroll(student=student, section_id=str(other.id), idempotency_key=idem1, correlation_id="test")

    # now enroll into section_basic should conflict (both day 1 overlap)
    idem2 = "idem-" + str(uuid.uuid4())
    with pytest.raises(BusinessRuleViolation) as e:
        EnrollmentService.enroll(student=student, section_id=str(section_basic.id), idempotency_key=idem2, correlation_id="test")
    assert e.value.code == "SCHEDULE_CONFLICT"


def test_enroll_fails_when_enrollment_window_closed(users, section_basic, term_open):
    # Close window by setting enroll_close_at in past
    term_open.enroll_close_at = timezone.now() - timezone.timedelta(seconds=1)
    term_open.save(update_fields=["enroll_close_at"])

    student = users["student1"]
    idem = "idem-" + str(uuid.uuid4())
    with pytest.raises(ConflictError) as e:
        EnrollmentService.enroll(student=student, section_id=str(section_basic.id), idempotency_key=idem, correlation_id="test")
    assert e.value.code == "ENROLLMENT_WINDOW_CLOSED"
