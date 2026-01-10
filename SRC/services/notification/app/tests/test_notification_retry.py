import uuid

import pytest
from celery.exceptions import Retry

from notification.tasks import handle_event

pytestmark = pytest.mark.django_db


def test_handle_event_retries_on_provider_failure(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("provider down")

    monkeypatch.setattr("notification.tasks.send_mock", boom)

    payload = {
        "event_id": str(uuid.uuid4()),
        "type": "EnrollmentCreated",
        "occurred_at": "2026-01-10T00:00:00Z",
        "version": 1,
        "correlation_id": "cid-1",
        "data": {"student_id": "1", "section_id": "2"},
    }

    with pytest.raises(Retry):
        handle_event(event=payload)
