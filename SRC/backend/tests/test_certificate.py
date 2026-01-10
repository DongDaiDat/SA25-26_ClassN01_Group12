import uuid

import pytest

from modules.assessment.infrastructure.models import GradeRecord
from modules.certificate.infrastructure.models import CertificateDefinition

pytestmark = pytest.mark.django_db


def test_issue_certificate_denied_when_condition_not_met(client_for, users, course_graph, section_basic):
    # definition requires course C101 passed >=5
    defn = CertificateDefinition.objects.create(
        code="CERT1",
        name="Completion",
        rules={"required_course_ids": [str(course_graph["C101"].id)], "min_grade": 5.0},
    )

    registrar = client_for("registrar")
    r = registrar.post(
        "/api/v1/certificate/issues/issue/",
        {"definition_id": str(defn.id), "student_id": str(users["student1"].id)},
        format="json",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "CERT_CONDITION_NOT_MET"


def test_issue_and_verify_certificate_success(client_for, users, course_graph, section_basic):
    defn = CertificateDefinition.objects.create(
        code="CERT2",
        name="Completion",
        rules={"required_course_ids": [str(course_graph["C101"].id)], "min_grade": 5.0},
    )

    # pass course
    GradeRecord.objects.create(
        student=users["student1"],
        section_id=uuid.uuid4(),
        term_id=section_basic.term_id,
        course_id=course_graph["C101"].id,
        grade_value=7.0,
        status=GradeRecord.STATUS_PUBLISHED,
        updated_by=users["instructor"],
    )

    registrar = client_for("registrar")
    r = registrar.post(
        "/api/v1/certificate/issues/issue/",
        {"definition_id": str(defn.id), "student_id": str(users["student1"].id)},
        format="json",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    assert r.status_code == 201
    verify_code = r.json()["data"]["verify_code"]

    # verify is AllowAny
    anon = client_for("student2")
    anon.credentials()  # remove auth header
    rv = anon.get(
        f"/api/v1/certificate/issues/verify/?code={verify_code}",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    assert rv.status_code == 200
    assert rv.json()["data"]["valid"] is True
