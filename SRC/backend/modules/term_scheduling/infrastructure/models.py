from django.db import models
from modules.shared.models import TimeStampedModel

class Term(TimeStampedModel):
    STATUS_DRAFT = "DRAFT"
    STATUS_OPEN = "OPEN"
    STATUS_LOCKED = "LOCKED"
    STATUS_CLOSED = "CLOSED"

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    enroll_open_at = models.DateTimeField()
    enroll_close_at = models.DateTimeField()
    status = models.CharField(max_length=20, default=STATUS_DRAFT)

    def __str__(self):
        return self.code
