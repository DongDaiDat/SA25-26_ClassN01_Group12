import uuid

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_login_success_returns_tokens(users):
    client = APIClient()
    r = client.post(
        "/api/v1/auth/login/",
        {"username": "student1", "password": "student123"},
        format="json",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    assert r.status_code == 200
    body = r.json()
    assert "access" in body and "refresh" in body


def test_login_invalid_password_fails(users):
    client = APIClient()
    r = client.post(
        "/api/v1/auth/login/",
        {"username": "student1", "password": "wrong"},
        format="json",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    assert r.status_code in (400, 401)


def test_refresh_returns_new_access(users):
    client = APIClient()
    login = client.post(
        "/api/v1/auth/login/",
        {"username": "student1", "password": "student123"},
        format="json",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    refresh = login.json()["refresh"]
    r = client.post(
        "/api/v1/auth/refresh/",
        {"refresh": refresh},
        format="json",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    assert r.status_code == 200
    assert "access" in r.json() and "refresh" in r.json()


def test_logout_blacklists_refresh(users):
    client = APIClient()
    login = client.post(
        "/api/v1/auth/login/",
        {"username": "student1", "password": "student123"},
        format="json",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    access = login.json()["access"]
    refresh = login.json()["refresh"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    r = client.post(
        "/api/v1/auth/logout/",
        {"refresh": refresh},
        format="json",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    assert r.status_code in (200, 201)

    # refreshing the same token should now fail
    r2 = client.post(
        "/api/v1/auth/refresh/",
        {"refresh": refresh},
        format="json",
        HTTP_X_REQUEST_ID=str(uuid.uuid4()),
    )
    assert r2.status_code in (401, 400)
