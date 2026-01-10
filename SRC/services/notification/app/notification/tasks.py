from celery import shared_task
from django.db import IntegrityError, transaction
from .models import NotificationMessage
from .provider import send_mock

def _build_message_from_event(event: dict):
    etype = event.get("type","")
    data = event.get("data", {}) or {}
    # Minimal template
    if etype == "EnrollmentCreated":
        subject = "Enrollment Confirmation"
        body = f"Student {data.get('student_id')} enrolled to section {data.get('section_id')}."
        to = data.get("student_email") or "student@example.com"
        return {"channel":"EMAIL","to": to, "subject": subject, "body": body}
    if etype == "EnrollmentCancelled":
        subject = "Enrollment Cancelled"
        body = f"Enrollment cancelled for section {data.get('section_id')}."
        to = data.get("student_email") or "student@example.com"
        return {"channel":"EMAIL","to": to, "subject": subject, "body": body}
    if etype == "CertificateIssued":
        subject = "Certificate Issued"
        body = f"Certificate {data.get('definition_code')} issued. Verify code: {data.get('verify_code')}."
        to = data.get("student_email") or "student@example.com"
        return {"channel":"EMAIL","to": to, "subject": subject, "body": body}
    return {"channel":"EMAIL","to":"student@example.com","subject":"Notification","body": str(event)}

@shared_task(bind=True, max_retries=5, default_retry_delay=10)
def handle_event(self, event: dict):
    event_id = event.get("event_id")
    event_type = event.get("type","")
    correlation_id = event.get("correlation_id","")
    msg_fields = _build_message_from_event(event)

    try:
        with transaction.atomic():
            msg = NotificationMessage.objects.create(
                event_id=event_id,
                event_type=event_type,
                correlation_id=correlation_id,
                channel=msg_fields["channel"],
                to=msg_fields["to"],
                subject=msg_fields.get("subject",""),
                body=msg_fields.get("body",""),
                status=NotificationMessage.STATUS_SENT,
                provider_response={},
            )
            resp = send_mock(msg.channel, msg.to, msg.subject, msg.body)
            msg.provider_response = resp
            msg.status = NotificationMessage.STATUS_SENT
            msg.save(update_fields=["provider_response","status","updated_at"])
            return {"id": str(msg.id), "status": msg.status}
    except IntegrityError:
        # duplicate event_id: idempotent
        return {"status": "DUPLICATE_IGNORED", "event_id": event_id}
    except Exception as exc:
        # Update or create failure record (without event_id uniqueness) is complicated; retry task
        raise self.retry(exc=exc)
