from dataclasses import dataclass
from typing import List
from datetime import time
from django.db import transaction

from modules.class_section.infrastructure.models import Section, ScheduleSlot, SectionInstructor
from modules.shared.exceptions import ConflictError, BusinessRuleViolation
from modules.term_scheduling.application.services import TermQueryService
from modules.course_catalog.application.services import CourseQueryService

@dataclass(frozen=True)
class SectionInfoDTO:
    section_id: str
    term_id: str
    course_id: str
    capacity: int
    enrolled_count: int
    status: str

@dataclass(frozen=True)
class SlotDTO:
    day_of_week: int
    start_time: time
    end_time: time

class SectionQueryService:
    @staticmethod
    def get_section_info(section_id: str) -> SectionInfoDTO:
        s = Section.objects.get(id=section_id)
        return SectionInfoDTO(
            section_id=str(s.id),
            term_id=str(s.term_id),
            course_id=str(s.course_id),
            capacity=s.capacity,
            enrolled_count=s.enrolled_count,
            status=s.status,
        )

    @staticmethod
    def get_section_slots(section_id: str) -> List[SlotDTO]:
        qs = ScheduleSlot.objects.filter(section_id=section_id).order_by("day_of_week","start_time")
        return [SlotDTO(day_of_week=x.day_of_week, start_time=x.start_time, end_time=x.end_time) for x in qs]

    @staticmethod
    def is_instructor_of_section(instructor_user_id: str, section_id: str) -> bool:
        return SectionInstructor.objects.filter(section_id=section_id, instructor_id=instructor_user_id).exists()

    @staticmethod
    def get_term_code(term_id: str) -> str:
        return TermQueryService.get(term_id).code

    @staticmethod
    def get_course_code(course_id: str) -> str:
        return CourseQueryService.get_course(course_id).code

class SectionCommandService:
    @staticmethod
    def validate_refs(*, term_id: str, course_id: str):
        # existence checks
        TermQueryService.get(term_id)
        CourseQueryService.get_course(course_id)

class SeatReservationService:
    @staticmethod
    @transaction.atomic
    def reserve_seat(section_id: str):
        s = Section.objects.select_for_update().get(id=section_id)
        if s.status != "ACTIVE":
            raise ConflictError("SECTION_INACTIVE", "Section is not active")
        if s.enrolled_count >= s.capacity:
            raise ConflictError("SECTION_FULL", "Section is full")
        s.enrolled_count += 1
        s.save(update_fields=["enrolled_count"])
        return s.enrolled_count

    @staticmethod
    @transaction.atomic
    def release_seat(section_id: str):
        s = Section.objects.select_for_update().get(id=section_id)
        if s.enrolled_count > 0:
            s.enrolled_count -= 1
            s.save(update_fields=["enrolled_count"])
        return s.enrolled_count
