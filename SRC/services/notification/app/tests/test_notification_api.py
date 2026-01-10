import uuid

import pytest
from notification.models import NotificationMessage

pytestmark = pytest.mark.django_db


def test_manual_send_creates_message(api_client):
    r = api_client.post(
        "/ms/notification/send/",
        {"channel": "EMAIL", "to": "u@example.com", "subject": "Hi", "body": "Test"},
        format="json",
    )
    assert r.status_code == 201
    data = r.json()
    assert data["to"] == "u@example.com"
    assert NotificationMessage.objects.count() == 1


def test_list_messages(api_client):
    NotificationMessage.objects.create(channel="EMAIL", to="a@x.com", subject="S", body="B")
    NotificationMessage.objects.create(channel="SMS", to="099", subject="", body="B2")

    r = api_client.get("/ms/notification/messages/")
    assert r.status_code == 200
    assert len(r.json()) >= 2
