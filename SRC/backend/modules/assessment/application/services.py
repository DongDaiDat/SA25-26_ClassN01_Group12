from typing import List, Dict, Any, Optional
from django.db import transaction
from django.utils import timezone

from modules.assessment.infrastructure.models import GradeRecord, GradeChangeLog, SectionGradePolicy
from modules.class_section.application.services import SectionQueryService
from modules.class_section.application.services import SectionQueryService as SQ
from modules.audit.application.services import AuditService
from modules.shared.exceptions import BusinessRuleViolation
from modules.shared.models import OutboxEvent

class AssessmentQueryService:
    @staticmethod
    def has_passed_course(student_id: str, course_id: str, min_grade: Optional[float] = None) -> bool:
        threshold = min_grade if min_grade is not None else 5.0  # assumption: pass >=5
        return GradeRecord.objects.filter(
            student_id=student_id,
            course_id=course_id,
            status=GradeRecord.STATUS_PUBLISHED,
            grade_value__gte=threshold,
        ).exists()

class GradeEntryService:
    @staticmethod
    @transaction.atomic
    def bulk_enter(*, instructor, section_id: str, grades: List[Dict[str, Any]], correlation_id: str):
        # ownership check
        if not SQ.is_instructor_of_section(str(instructor.id), section_id) and instructor.role not in ("ADMIN","REGISTRAR"):
            raise BusinessRuleViolation("FORBIDDEN", "Instructor not assigned to section", status_code=403)

        sec = SectionQueryService.get_section_info(section_id)
        policy, _ = SectionGradePolicy.objects.get_or_create(section_id=section_id)
        if policy.grading_status != "OPEN":
            raise BusinessRuleViolation("GRADING_LOCKED", "Grading is locked", status_code=409)

        results = []
        for row in grades:
            student_id = row["student_id"]
            value = row.get("grade_value")
            if value is not None and (value < 0 or value > 10):
                raise BusinessRuleViolation("INVALID_GRADE", "Grade must be between 0 and 10")
            gr, _ = GradeRecord.objects.update_or_create(
                student_id=student_id,
                section_id=section_id,
                defaults={
                    "term_id": sec.term_id,
                    "course_id": sec.course_id,
                    "grade_value": value,
                    "grade_scale": "0-10",
                    "status": GradeRecord.STATUS_DRAFT,
                    "updated_by": instructor,
                },
            )
            results.append({"student_id": student_id, "grade_record_id": str(gr.id), "status": gr.status})
        AuditService.log(actor=instructor, action="GRADE_BULK_ENTER", entity_type="Section", entity_id=str(section_id),
                         after={"count": len(results)}, correlation_id=correlation_id)
        return results

class GradePublishService:
    @staticmethod
    @transaction.atomic
    def publish(*, actor, section_id: str, correlation_id: str):
        if actor.role not in ("ADMIN","REGISTRAR","INSTRUCTOR"):
            raise BusinessRuleViolation("FORBIDDEN", "Not allowed", status_code=403)
        if actor.role == "INSTRUCTOR" and not SQ.is_instructor_of_section(str(actor.id), section_id):
            raise BusinessRuleViolation("FORBIDDEN", "Instructor not assigned to section", status_code=403)

        policy, _ = SectionGradePolicy.objects.select_for_update().get_or_create(section_id=section_id)
        policy.publish_status = "PUBLISHED"
        policy.save(update_fields=["publish_status"])

        updated = GradeRecord.objects.filter(section_id=section_id).update(status=GradeRecord.STATUS_PUBLISHED, updated_at=timezone.now())
        AuditService.log(actor=actor, action="GRADE_PUBLISH", entity_type="Section", entity_id=str(section_id),
                         after={"published_records": updated}, correlation_id=correlation_id)
        OutboxEvent.objects.create(
            event_type="GradePublished",
            version=1,
            correlation_id=correlation_id,
            payload={"section_id": str(section_id), "published_by": str(actor.id)},
        )
        return {"section_id": str(section_id), "published_records": updated}

class GradeChangeService:
    @staticmethod
    @transaction.atomic
    def change(*, actor, grade_id: str, new_value: float, reason: str, correlation_id: str):
        if not reason:
            raise BusinessRuleViolation("REASON_REQUIRED", "Reason is required")
        if new_value < 0 or new_value > 10:
            raise BusinessRuleViolation("INVALID_GRADE", "Grade must be between 0 and 10")
        gr = GradeRecord.objects.select_for_update().get(id=grade_id)
        # permission: registrar/admin or instructor owner of section
        if actor.role == "INSTRUCTOR" and not SQ.is_instructor_of_section(str(actor.id), str(gr.section_id)):
            raise BusinessRuleViolation("FORBIDDEN", "Instructor not assigned to section", status_code=403)
        if actor.role not in ("ADMIN","REGISTRAR","INSTRUCTOR"):
            raise BusinessRuleViolation("FORBIDDEN", "Not allowed", status_code=403)

        old = gr.grade_value
        gr.grade_value = new_value
        gr.updated_by = actor
        gr.save(update_fields=["grade_value","updated_by","updated_at"])

        GradeChangeLog.objects.create(grade_record=gr, old_value=old, new_value=new_value, reason=reason, changed_by=actor)
        AuditService.log(actor=actor, action="GRADE_CHANGE", entity_type="GradeRecord", entity_id=str(gr.id),
                         before={"grade_value": old}, after={"grade_value": new_value, "reason": reason}, correlation_id=correlation_id)
        return {"id": str(gr.id), "old_value": old, "new_value": new_value}
