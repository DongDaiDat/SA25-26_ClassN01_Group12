import uuid
from django.db import models

class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class OutboxEvent(TimeStampedModel):
    STATUS_NEW = "NEW"
    STATUS_PUBLISHED = "PUBLISHED"
    STATUS_FAILED = "FAILED"

    status = models.CharField(max_length=20, default=STATUS_NEW)
    event_type = models.CharField(max_length=100)
    version = models.IntegerField(default=1)
    correlation_id = models.CharField(max_length=100, blank=True, default="")
    payload = models.JSONField()
    published_at = models.DateTimeField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["status", "event_type", "created_at"])]
