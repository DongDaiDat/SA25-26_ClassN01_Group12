import uuid
from datetime import date, timedelta, time

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from modules.term_scheduling.infrastructure.models import Term
from modules.course_catalog.infrastructure.models import Course, CoursePrerequisite
from modules.class_section.infrastructure.models import Section, ScheduleSlot, Room, SectionInstructor


@pytest.fixture
def user_factory(db):
    User = get_user_model()

    def _create(username: str, role: str, password: str = "pass123", **kwargs):
        u = User.objects.create_user(username=username, password=password, role=role, email=kwargs.get("email", ""))
        return u

    return _create


@pytest.fixture
def users(user_factory):
    return {
        "admin": user_factory("admin", "ADMIN", "admin123"),
        "registrar": user_factory("registrar", "REGISTRAR", "registrar123"),
        "instructor": user_factory("instructor", "INSTRUCTOR", "instructor123"),
        "student1": user_factory("student1", "STUDENT", "student123"),
        "student2": user_factory("student2", "STUDENT", "student123"),
        "manager": user_factory("manager", "MANAGER", "manager123"),
    }


def _auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    client.defaults["HTTP_X_REQUEST_ID"] = str(uuid.uuid4())
    return client


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authed_client(users):
    # default student
    return _auth_client(users["student1"])


@pytest.fixture
def client_for(users):
    def _get(role_key: str):
        return _auth_client(users[role_key])
    return _get


@pytest.fixture
def term_open(db):
    now = timezone.now()
    return Term.objects.create(
        code="2026A",
        name="Spring 2026",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=120),
        enroll_open_at=now - timedelta(days=1),
        enroll_close_at=now + timedelta(days=1),
        status=Term.STATUS_OPEN,
    )


@pytest.fixture
def term_closed(db):
    now = timezone.now()
    return Term.objects.create(
        code="2025B",
        name="Fall 2025",
        start_date=date.today() - timedelta(days=200),
        end_date=date.today() - timedelta(days=80),
        enroll_open_at=now - timedelta(days=10),
        enroll_close_at=now - timedelta(days=5),
        status=Term.STATUS_OPEN,
    )


@pytest.fixture
def course_graph(db):
    # C102 requires C101
    c101 = Course.objects.create(code="C101", name="Intro", credits=3)
    c102 = Course.objects.create(code="C102", name="Advanced", credits=3)
    CoursePrerequisite.objects.create(course=c102, prereq_course=c101, min_grade=5.0)
    return {"C101": c101, "C102": c102}


@pytest.fixture
def section_basic(db, term_open, course_graph, users):
    sec = Section.objects.create(
        term_id=term_open.id,
        course_id=course_graph["C102"].id,
        section_code="S1",
        capacity=1,
        enrolled_count=0,
        status="ACTIVE",
    )
    room = Room.objects.create(code="R1", name="Room 1")
    ScheduleSlot.objects.create(section=sec, day_of_week=1, start_time=time(9, 0), end_time=time(10, 0), room=room)
    SectionInstructor.objects.create(section=sec, instructor=users["instructor"])
    return sec
