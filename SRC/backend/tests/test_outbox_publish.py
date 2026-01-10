import pytest

from modules.shared.models import OutboxEvent
from modules.shared.tasks import publish_outbox

pytestmark = pytest.mark.django_db


def test_outbox_publisher_sends_task_and_marks_published(monkeypatch, settings):
    captured = {}

    def fake_send_task(name, kwargs=None, **_):
        captured["name"] = name
        captured["kwargs"] = kwargs
        return None

    monkeypatch.setattr("modules.shared.tasks.current_app.send_task", fake_send_task)

    ev = OutboxEvent.objects.create(
        event_type="EnrollmentCreated",
        version=1,
        correlation_id="cid-1",
        payload={"student_id": "1", "section_id": "S"},
    )

    res = publish_outbox()
    assert res["sent"] == 1

    ev.refresh_from_db()
    assert ev.status == OutboxEvent.STATUS_PUBLISHED

    assert captured["name"] == settings.NOTIFICATION_CELERY_TASK
    event = captured["kwargs"]["event"]
    assert event["event_id"] == str(ev.id)
    assert event["type"] == "EnrollmentCreated"
    assert event["version"] == 1
    assert event["correlation_id"] == "cid-1"
    assert event["data"]["student_id"] == "1"
