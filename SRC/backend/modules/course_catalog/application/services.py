from dataclasses import dataclass
from typing import List, Optional
from modules.course_catalog.infrastructure.models import Course, CoursePrerequisite
from modules.shared.exceptions import BusinessRuleViolation

@dataclass(frozen=True)
class PrereqRuleDTO:
    prereq_course_id: str
    prereq_course_code: str
    min_grade: Optional[float]

class CourseQueryService:
    @staticmethod
    def get_course(course_id: str) -> Course:
        return Course.objects.get(id=course_id)

    @staticmethod
    def get_prereq_rules(course_id: str) -> List[PrereqRuleDTO]:
        qs = CoursePrerequisite.objects.select_related("prereq_course").filter(course_id=course_id)
        return [
            PrereqRuleDTO(
                prereq_course_id=str(p.prereq_course_id),
                prereq_course_code=p.prereq_course.code,
                min_grade=p.min_grade,
            )
            for p in qs
        ]

class CoursePrereqService:
    @staticmethod
    def set_prerequisites(course_id: str, prereq_ids: List[str], *, actor=None, correlation_id=""):
        course = Course.objects.get(id=course_id)
        # prevent self prerequisite
        if str(course.id) in [str(x) for x in prereq_ids]:
            raise BusinessRuleViolation("INVALID_PREREQ", "Course cannot require itself")
        # simple cycle check (depth 2) to keep it light
        for prereq_id in prereq_ids:
            if CoursePrerequisite.objects.filter(course_id=prereq_id, prereq_course_id=course_id).exists():
                raise BusinessRuleViolation("PREREQ_CYCLE", "Prerequisite cycle detected")
        CoursePrerequisite.objects.filter(course=course).exclude(prereq_course_id__in=prereq_ids).delete()
        existing = set(CoursePrerequisite.objects.filter(course=course).values_list("prereq_course_id", flat=True))
        for pid in prereq_ids:
            if pid not in existing:
                CoursePrerequisite.objects.create(course=course, prereq_course_id=pid)
        return CourseQueryService.get_prereq_rules(course_id)
