import uuid

import pytest

pytestmark = pytest.mark.django_db


def test_course_unique_code_constraint(client_for):
    client = client_for("admin")
    payload = {"code": "C-UNIQ", "name": "Course", "credits": 3, "status": "ACTIVE"}
    r1 = client.post("/api/v1/course-catalog/courses/", payload, format="json", HTTP_X_REQUEST_ID=str(uuid.uuid4()))
    assert r1.status_code == 201
    r2 = client.post("/api/v1/course-catalog/courses/", payload, format="json", HTTP_X_REQUEST_ID=str(uuid.uuid4()))
    assert r2.status_code in (400, 409)


def test_program_search_and_pagination_smoke(client_for):
    client = client_for("admin")
    for i in range(15):
        client.post(
            "/api/v1/program/programs/",
            {"code": f"PRG{i}", "name": f"Program {i}", "status": "ACTIVE"},
            format="json",
            HTTP_X_REQUEST_ID=str(uuid.uuid4()),
        )
    r = client.get("/api/v1/program/programs/?search=Program", HTTP_X_REQUEST_ID=str(uuid.uuid4()))
    assert r.status_code == 200
    # response envelope
    assert isinstance(r.json().get("data"), list)
