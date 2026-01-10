import uuid

import pytest

from modules.assessment.infrastructure.models import GradeRecord

pytestmark = pytest.mark.django_db


def test_instructor_bulk_enter_grades_success(client_for, section_basic, users):
    instructor = users["instructor"]
    client = client_for("instructor")
    payload = {
        "section_id": str(section_basic.id),
        "grades": [
            {"student_id": str(users["student1"].id), "grade_value": 8.0},
        ],
    }
    r = client.post(
        "/api/v1/assessment/grades/bulk_enter/",
        payload,
        format="json",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1
    gr = GradeRecord.objects.get(student=users["student1"], section_id=section_basic.id)
    assert gr.status == GradeRecord.STATUS_DRAFT


def test_student_cannot_bulk_enter_grades(client_for, section_basic, users):
    client = client_for("student1")
    payload = {
        "section_id": str(section_basic.id),
        "grades": [{"student_id": str(users["student1"].id), "grade_value": 8.0}],
    }
    r = client.post(
        "/api/v1/assessment/grades/bulk_enter/",
        payload,
        format="json",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    assert r.status_code == 403


def test_publish_then_student_can_view_grade(client_for, section_basic, users):
    # instructor enter
    instr_client = client_for("instructor")
    instr_client.post(
        "/api/v1/assessment/grades/bulk_enter/",
        {"section_id": str(section_basic.id), "grades": [{"student_id": str(users["student1"].id), "grade_value": 9.0}]},
        format="json",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )

    # publish
    r = instr_client.post(
        "/api/v1/assessment/grades/publish/",
        {"section_id": str(section_basic.id)},
        format="json",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    assert r.status_code == 200

    # student sees only own
    student_client = client_for("student1")
    r2 = student_client.get("/api/v1/assessment/grades/", HTTP_X_REQUEST_ID=str(uuid.uuid4()))
    assert r2.status_code == 200
    rows = r2.json()["data"]
    assert any(x["section_id"] == str(section_basic.id) and x["status"] == "PUBLISHED" for x in rows)
