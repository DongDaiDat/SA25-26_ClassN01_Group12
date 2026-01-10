from django.db import models
from modules.shared.models import TimeStampedModel

class Course(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    credits = models.IntegerField()
    status = models.CharField(max_length=20, default="ACTIVE")  # ACTIVE/INACTIVE
    description = models.TextField(blank=True, default="")

    class Meta:
        indexes = [models.Index(fields=["code"], name="course_code_idx")]

class CoursePrerequisite(TimeStampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="prerequisites")
    prereq_course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="required_for")
    min_grade = models.FloatField(null=True, blank=True)  # optional

    class Meta:
        unique_together = [("course","prereq_course")]
