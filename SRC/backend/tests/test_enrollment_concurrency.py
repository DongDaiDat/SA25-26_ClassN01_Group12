import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
from django.db import close_old_connections

from modules.assessment.infrastructure.models import GradeRecord
from modules.enrollment.application.services import EnrollmentService
from modules.shared.exceptions import ConflictError

pytestmark = pytest.mark.django_db(transaction=True)


def test_concurrent_enrollment_does_not_overbook(users, section_basic, course_graph):
    # capacity is 1 in fixture section_basic
    s1 = users["student1"]
    s2 = users["student2"]

    # both satisfy prerequisite
    for student in (s1, s2):
        GradeRecord.objects.create(
            student=student,
            section_id=uuid.uuid4(),
            term_id=section_basic.term_id,
            course_id=course_graph["C101"].id,
            grade_value=7.0,
            status=GradeRecord.STATUS_PUBLISHED,
            updated_by=student,
        )

    def _attempt(student):
        close_old_connections()
        try:
            res = EnrollmentService.enroll(
                student=student,
                section_id=str(section_basic.id),
                idempotency_key=f"idem-{student.username}-{uuid.uuid4()}",
                correlation_id="concurrency",
            )
            return ("OK", res)
        except ConflictError as e:
            return ("FAIL", e.code)

    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = [ex.submit(_attempt, s1), ex.submit(_attempt, s2)]
        results = [f.result() for f in as_completed(futures)]

    ok = [r for r in results if r[0] == "OK"]
    fail = [r for r in results if r[0] == "FAIL"]

    assert len(ok) == 1
    assert len(fail) == 1
    assert fail[0][1] in ("SECTION_FULL",)

    # enrolled_count must not exceed capacity
    sec = section_basic.__class__.objects.get(id=section_basic.id)
    assert sec.enrolled_count == 1
