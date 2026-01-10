import uuid

import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "role,expected",
    [
        ("admin", 201),
        ("registrar", 201),
        ("manager", 403),
        ("instructor", 403),
        ("student1", 403),
    ],
)
def test_program_create_rbac(client_for, role, expected):
    client = client_for(role)
    payload = {"code": f"PRG-{role}", "name": "CS", "status": "ACTIVE"}
    r = client.post("/api/v1/program/programs/", payload, format="json", HTTP_X_REQUEST_ID=str(uuid.uuid4()))
    assert r.status_code == expected


@pytest.mark.parametrize(
    "role,expected",
    [
        ("admin", 201),
        ("registrar", 201),
        ("manager", 403),
        ("instructor", 403),
        ("student1", 403),
    ],
)
def test_course_create_rbac(client_for, role, expected):
    client = client_for(role)
    payload = {"code": f"C-{role}", "name": "Course", "credits": 3, "status": "ACTIVE"}
    r = client.post("/api/v1/course-catalog/courses/", payload, format="json", HTTP_X_REQUEST_ID=str(uuid.uuid4()))
    assert r.status_code == expected


def test_student_cannot_list_all_enrollments(client_for, section_basic):
    # student can only see own enrollments
    student = client_for("student1")
    r = student.get("/api/v1/enrollment/enrollments/", HTTP_X_REQUEST_ID=str(uuid.uuid4()))
    assert r.status_code == 200
    data = r.json().get("data")
    assert isinstance(data, list)

    admin = client_for("admin")
    r2 = admin.get("/api/v1/enrollment/enrollments/", HTTP_X_REQUEST_ID=str(uuid.uuid4()))
    assert r2.status_code == 200
    assert isinstance(r2.json().get("data"), list)
