import uuid

import pytest

from modules.assessment.infrastructure.models import GradeRecord
from modules.audit.infrastructure.models import AuditLog

pytestmark = pytest.mark.django_db


def test_enrollment_creates_audit_log(client_for, section_basic, users, course_graph):
    # prereq pass
    GradeRecord.objects.create(
        student=users["student1"],
        section_id=uuid.uuid4(),
        term_id=section_basic.term_id,
        course_id=course_graph["C101"].id,
        grade_value=7.0,
        status=GradeRecord.STATUS_PUBLISHED,
        updated_by=users["student1"],
    )
    client = client_for("student1")
    cid = str(uuid.uuid4())
    r = client.post(
        "/api/v1/enrollment/enrollments/",
        {"section_id": str(section_basic.id)},
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()),
        HTTP_X_REQUEST_ID=cid,
    )
    assert r.status_code == 201
    enr_id = r.json()["data"]["id"]

    log = AuditLog.objects.filter(action="ENROLLMENT_CREATE", entity_id=enr_id).first()
    assert log is not None
    assert log.correlation_id == cid
    assert log.actor_id == users["student1"].id
