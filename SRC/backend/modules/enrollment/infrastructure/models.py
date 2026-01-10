from django.db import models
from django.conf import settings
from modules.shared.models import TimeStampedModel

class Enrollment(TimeStampedModel):
    STATUS_ACTIVE = "ACTIVE"
    STATUS_CANCELED = "CANCELED"

    SOURCE_NORMAL = "NORMAL"
    SOURCE_OVERRIDE = "OVERRIDE"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="enrollments")
    section_id = models.UUIDField()
    term_id = models.UUIDField()
    course_id = models.UUIDField()
    status = models.CharField(max_length=20, default=STATUS_ACTIVE)
    source = models.CharField(max_length=20, default=SOURCE_NORMAL)
    reason = models.CharField(max_length=255, blank=True, default="")
    canceled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("student","section_id")]
        indexes = [
            models.Index(fields=["student","status"], name="enr_student_status"),
            models.Index(fields=["term_id"], name="enr_term_idx"),
        ]

class EnrollmentAttempt(TimeStampedModel):
    idempotency_key = models.CharField(max_length=80, unique=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    section_id = models.UUIDField()
    result = models.JSONField(default=dict)

class OverrideDecision(TimeStampedModel):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="override_decisions")
    section_id = models.UUIDField()
    bypass_flags = models.JSONField(default=dict)
    reason = models.CharField(max_length=255)
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="approved_overrides")
