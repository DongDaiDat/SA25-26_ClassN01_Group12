from django.db import models
from django.conf import settings
from modules.shared.models import TimeStampedModel

class GradeRecord(TimeStampedModel):
    STATUS_DRAFT = "DRAFT"
    STATUS_PUBLISHED = "PUBLISHED"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="grades")
    section_id = models.UUIDField()
    term_id = models.UUIDField()
    course_id = models.UUIDField()

    grade_value = models.FloatField(null=True, blank=True)  # numeric 0-10 (assumption)
    grade_scale = models.CharField(max_length=20, default="0-10")
    status = models.CharField(max_length=20, default=STATUS_DRAFT)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="grade_updates")

    class Meta:
        unique_together = [("student","section_id")]
        indexes = [
            models.Index(fields=["student","course_id","status"], name="grade_student_course"),
        ]

class GradeChangeLog(TimeStampedModel):
    grade_record = models.ForeignKey(GradeRecord, on_delete=models.CASCADE, related_name="changes")
    old_value = models.FloatField(null=True, blank=True)
    new_value = models.FloatField(null=True, blank=True)
    reason = models.CharField(max_length=255)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

class SectionGradePolicy(TimeStampedModel):
    section_id = models.UUIDField(unique=True)
    grading_status = models.CharField(max_length=20, default="OPEN")  # OPEN/LOCKED
    publish_status = models.CharField(max_length=20, default="HIDDEN")  # HIDDEN/PUBLISHED
