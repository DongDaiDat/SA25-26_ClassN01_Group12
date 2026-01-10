from django.db import models
from django.conf import settings
from modules.shared.models import TimeStampedModel

class Room(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.code

class Section(TimeStampedModel):
    term_id = models.UUIDField()
    course_id = models.UUIDField()
    section_code = models.CharField(max_length=20)
    capacity = models.IntegerField()
    enrolled_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="ACTIVE")  # ACTIVE/CANCELED

    class Meta:
        unique_together = [("term_id","course_id","section_code")]
        indexes = [
            models.Index(fields=["term_id","course_id"], name="section_term_course"),
        ]

class SectionInstructor(TimeStampedModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="instructors")
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="teaching_sections")

    class Meta:
        unique_together = [("section","instructor")]

class ScheduleSlot(TimeStampedModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="schedule_slots")
    day_of_week = models.IntegerField()  # 1=Mon..7=Sun
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.ForeignKey(Room, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        indexes = [
            models.Index(fields=["section","day_of_week"], name="slot_section_day"),
        ]
