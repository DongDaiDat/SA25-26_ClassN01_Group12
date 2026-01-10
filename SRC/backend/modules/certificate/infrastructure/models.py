from django.db import models
from django.conf import settings
from modules.shared.models import TimeStampedModel

class CertificateDefinition(TimeStampedModel):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    rules = models.JSONField(default=dict)  # {required_course_ids:[], min_grade:5}

class CertificateIssue(TimeStampedModel):
    definition = models.ForeignKey(CertificateDefinition, on_delete=models.PROTECT, related_name="issues")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="certificates")
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="issued_certificates")
    verify_code = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, default="ISSUED")  # ISSUED/REVOKED
    metadata = models.JSONField(default=dict)
