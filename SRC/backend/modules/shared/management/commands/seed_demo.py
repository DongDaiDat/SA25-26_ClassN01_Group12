from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date, time

from modules.course_catalog.infrastructure.models import Course
from modules.term_scheduling.infrastructure.models import Term
from modules.class_section.infrastructure.models import Section, ScheduleSlot, SectionInstructor
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Seed demo data: courses, one open term, sections, schedule, instructor assignment"

    def handle(self, *args, **options):
        # Courses
        c1, _ = Course.objects.get_or_create(code="CS101", defaults={"name":"Intro to CS", "credits":3})
        c2, _ = Course.objects.get_or_create(code="CS102", defaults={"name":"Data Structures", "credits":3})
        # Term
        now = timezone.now()
        term, _ = Term.objects.get_or_create(
            code="2026S1",
            defaults={
                "name":"Semester 1/2026",
                "start_date": date.today(),
                "end_date": date.today(),
                "enroll_open_at": now - timedelta(days=1),
                "enroll_close_at": now + timedelta(days=30),
                "status": Term.STATUS_OPEN,
            },
        )
        # Sections
        s1, _ = Section.objects.get_or_create(term_id=term.id, course_id=c1.id, section_code="A", defaults={"capacity": 50})
        s2, _ = Section.objects.get_or_create(term_id=term.id, course_id=c2.id, section_code="A", defaults={"capacity": 50})
        ScheduleSlot.objects.get_or_create(section=s1, day_of_week=1, start_time=time(9,0), end_time=time(10,30))
        ScheduleSlot.objects.get_or_create(section=s2, day_of_week=3, start_time=time(9,0), end_time=time(10,30))

        instructor = User.objects.filter(role=User.ROLE_INSTRUCTOR).first()
        if instructor:
            SectionInstructor.objects.get_or_create(section=s1, instructor=instructor)
            SectionInstructor.objects.get_or_create(section=s2, instructor=instructor)

        self.stdout.write(self.style.SUCCESS("Seeded demo data. Term=2026S1, Courses=CS101, CS102"))
