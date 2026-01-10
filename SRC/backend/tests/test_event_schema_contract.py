import pytest

from modules.shared.models import OutboxEvent
from modules.shared.tasks import publish_outbox

pytestmark = pytest.mark.django_db


def test_event_contract_fields_required(monkeypatch, settings):
    captured = {}

    def fake_send_task(name, kwargs=None, **_):
        captured["event"] = (kwargs or {}).get("event")
        return None

    monkeypatch.setattr("modules.shared.tasks.current_app.send_task", fake_send_task)

    ev = OutboxEvent.objects.create(
        event_type="EnrollmentCreated",
        version=1,
        correlation_id="cid-xyz",
        payload={"student_id": "1", "section_id": "2", "term_id": "3", "course_id": "4"},
    )
    publish_outbox(batch_size=1)

    event = captured["event"]
    assert event is not None
    for key in ("event_id", "type", "occurred_at", "version", "correlation_id", "data"):
        assert key in event

    assert event["type"] == "EnrollmentCreated"
    for k in ("student_id", "section_id", "term_id", "course_id"):
        assert k in event["data"]
    assert event["version"] == 1
    assert event["event_id"] == str(ev.id)
