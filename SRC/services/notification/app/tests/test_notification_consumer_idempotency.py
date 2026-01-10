import uuid

import pytest

from notification.models import NotificationMessage
from notification.tasks import handle_event

pytestmark = pytest.mark.django_db


def test_handle_event_is_idempotent_on_event_id(monkeypatch):
    # make provider deterministic
    monkeypatch.setattr("notification.tasks.send_mock", lambda *a, **k: {"ok": True})

    event_id = uuid.uuid4()
    payload = {
        "event_id": str(event_id),
        "type": "EnrollmentCreated",
        "occurred_at": "2026-01-10T00:00:00Z",
        "version": 1,
        "correlation_id": "cid-1",
        "data": {"student_id": "1", "section_id": "2"},
    }

    r1 = handle_event(event=payload)
    assert NotificationMessage.objects.count() == 1

    r2 = handle_event(event=payload)
    assert NotificationMessage.objects.count() == 1
    assert r2["status"] == "DUPLICATE_IGNORED"
