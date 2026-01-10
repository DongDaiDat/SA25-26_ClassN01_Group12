from django.db import models
from modules.shared.models import TimeStampedModel

class Program(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default="ACTIVE")  # ACTIVE/INACTIVE

    def __str__(self):
        return f"{self.code} - {self.name}"

class CurriculumVersion(TimeStampedModel):
    STATUS_DRAFT = "DRAFT"
    STATUS_PUBLISHED = "PUBLISHED"
    STATUS_ARCHIVED = "ARCHIVED"

    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name="curricula")
    version_code = models.CharField(max_length=20)  # e.g., 2025
    status = models.CharField(max_length=20, default=STATUS_DRAFT)
    effective_year = models.IntegerField()
    notes = models.TextField(blank=True, default="")

    class Meta:
        unique_together = [("program","version_code")]

class CurriculumNode(TimeStampedModel):
    curriculum = models.ForeignKey(CurriculumVersion, on_delete=models.CASCADE, related_name="nodes")
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")
    node_type = models.CharField(max_length=30, default="GROUP")  # GROUP/REQUIREMENT
    title = models.CharField(max_length=255)
    sort_order = models.IntegerField(default=0)

class CurriculumRule(TimeStampedModel):
    node = models.ForeignKey(CurriculumNode, on_delete=models.CASCADE, related_name="rules")
    rule_type = models.CharField(max_length=50)  # required_credits, required_courses, elective_pool
    params = models.JSONField(default=dict)
