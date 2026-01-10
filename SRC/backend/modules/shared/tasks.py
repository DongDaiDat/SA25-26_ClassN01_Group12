from celery import shared_task
from django.utils import timezone
from django.conf import settings
from celery import current_app

from .models import OutboxEvent

@shared_task
def publish_outbox(batch_size: int = 50):
    qs = OutboxEvent.objects.filter(status=OutboxEvent.STATUS_NEW).order_by("created_at")[:batch_size]
    sent = 0
    for ev in qs:
        try:
            # Send event as Celery task to notification service (task name configured via env)
            current_app.send_task(
                settings.NOTIFICATION_CELERY_TASK,
                kwargs={"event": {
                    "event_id": str(ev.id),
                    "type": ev.event_type,
                    "occurred_at": ev.created_at.isoformat(),
                    "version": ev.version,
                    "correlation_id": ev.correlation_id,
                    "data": ev.payload,
                }},
            )
            ev.status = OutboxEvent.STATUS_PUBLISHED
            ev.published_at = timezone.now()
            ev.save(update_fields=["status", "published_at"])
            sent += 1
        except Exception:
            ev.retry_count += 1
            ev.status = OutboxEvent.STATUS_FAILED if ev.retry_count >= 10 else OutboxEvent.STATUS_NEW
            ev.save(update_fields=["retry_count", "status"])
    return {"sent": sent}
