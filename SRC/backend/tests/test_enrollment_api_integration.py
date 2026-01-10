import uuid

import pytest

from modules.assessment.infrastructure.models import GradeRecord
from modules.shared.models import OutboxEvent

pytestmark = pytest.mark.django_db


def test_enroll_requires_idempotency_key(client_for, section_basic):
    client = client_for("student1")
    r = client.post(
        "/api/v1/enrollment/enrollments/",
        {"section_id": str(section_basic.id)},
        format="json",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    assert r.status_code == 400
    body = r.json()
    assert body["error"]["code"] == "IDEMPOTENCY_REQUIRED"


def test_enroll_success_creates_outbox_and_audit(client_for, section_basic, users, course_graph):
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

    client = client_for("student1")
    idem = str(uuid.uuid4())
    r = client.post(
        "/api/v1/enrollment/enrollments/",
        {"section_id": str(section_basic.id)},
        format="json",
        HTTP_IDEMPOTENCY_KEY=idem,
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    assert r.status_code == 201
    enr_id = r.json()["data"]["id"]

    evt = OutboxEvent.objects.filter(event_type="EnrollmentCreated").order_by("-created_at").first()
    assert evt is not None
    assert evt.payload["student_id"] == str(student.id)
    assert evt.payload["section_id"] == str(section_basic.id)

    # idempotent retry should return same enrollment id
    r2 = client.post(
        "/api/v1/enrollment/enrollments/",
        {"section_id": str(section_basic.id)},
        format="json",
        HTTP_IDEMPOTENCY_KEY=idem,
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    assert r2.status_code == 201
    assert r2.json()["data"]["id"] == enr_id


def test_cancel_enrollment_releases_seat(client_for, section_basic, users, course_graph):
    student = users["student1"]
    GradeRecord.objects.create(
        student=student,
        section_id=uuid.uuid4(),
        term_id=section_basic.term_id,
        course_id=course_graph["C101"].id,
        grade_value=7.0,
        status=GradeRecord.STATUS_PUBLISHED,
        updated_by=student,
    )

    client = client_for("student1")
    r = client.post(
        "/api/v1/enrollment/enrollments/",
        {"section_id": str(section_basic.id)},
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()),
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    enr_id = r.json()["data"]["id"]

    before = section_basic.__class__.objects.get(id=section_basic.id).enrolled_count
    assert before == 1

    r2 = client.delete(
        f"/api/v1/enrollment/enrollments/{enr_id}/",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    assert r2.status_code == 200

    after = section_basic.__class__.objects.get(id=section_basic.id).enrolled_count
    assert after == 0
