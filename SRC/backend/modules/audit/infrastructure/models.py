from django.db import models
from django.conf import settings
from modules.shared.models import TimeStampedModel

class AuditLog(TimeStampedModel):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    action = models.CharField(max_length=120)
    entity_type = models.CharField(max_length=120, blank=True, default="")
    entity_id = models.CharField(max_length=64, blank=True, default="")
    result = models.CharField(max_length=20, default="SUCCESS")  # SUCCESS/DENY/FAIL
    reason_code = models.CharField(max_length=80, blank=True, default="")
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)
    correlation_id = models.CharField(max_length=100, blank=True, default="")
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=["action","created_at"], name="audit_action_time"),
            models.Index(fields=["entity_type","entity_id"], name="audit_entity"),
        ]
