from dataclasses import asdict
from datetime import datetime, timezone
from django.db import transaction
from django.utils import timezone as djtz

from modules.enrollment.infrastructure.models import Enrollment, EnrollmentAttempt, OverrideDecision
from modules.shared.exceptions import BusinessRuleViolation, ConflictError
from modules.audit.application.services import AuditService
from modules.shared.models import OutboxEvent

from modules.term_scheduling.application.services import TermQueryService
from modules.course_catalog.application.services import CourseQueryService
from modules.class_section.application.services import SectionQueryService, SeatReservationService
from modules.assessment.application.services import AssessmentQueryService

def _now():
    return djtz.now()

def _parse_iso(dt_str: str):
    return datetime.fromisoformat(dt_str.replace("Z","+00:00"))

def _time_overlap(a_start, a_end, b_start, b_end):
    return (a_start < b_end) and (b_start < a_end)

class EnrollmentService:
    EVENT_ENROLLMENT_CREATED = "EnrollmentCreated"
    EVENT_ENROLLMENT_CANCELLED = "EnrollmentCancelled"

    @staticmethod
    def enroll(*, student, section_id: str, idempotency_key: str, correlation_id: str):
        # Idempotency first
        attempt = EnrollmentAttempt.objects.filter(idempotency_key=idempotency_key).first()
        if attempt:
            return attempt.result

        with transaction.atomic():
            EnrollmentAttempt.objects.create(idempotency_key=idempotency_key, student=student, section_id=section_id, result={})
            sec = SectionQueryService.get_section_info(section_id)
            term = TermQueryService.get_status(sec.term_id)

            # term open + within window
            if term.status != "OPEN":
                raise ConflictError("TERM_LOCKED", "Term is not open for enrollment")
            now = _now()
            if not (_parse_iso(term.enroll_open_at) <= now <= _parse_iso(term.enroll_close_at)):
                raise ConflictError("ENROLLMENT_WINDOW_CLOSED", "Enrollment window is closed")

            # prerequisite check
            prereqs = CourseQueryService.get_prereq_rules(sec.course_id)
            for p in prereqs:
                ok = AssessmentQueryService.has_passed_course(
                    student_id=str(student.id),
                    course_id=p.prereq_course_id,
                    min_grade=p.min_grade,
                )
                if not ok:
                    raise BusinessRuleViolation("PREREQ_NOT_MET", f"Missing prerequisite: {p.prereq_course_code}")

            # schedule conflict: compare slots with existing enrollments in same term
            new_slots = SectionQueryService.get_section_slots(section_id)
            existing = Enrollment.objects.filter(student=student, term_id=sec.term_id, status=Enrollment.STATUS_ACTIVE).values_list("section_id", flat=True)
            for s_id in existing:
                slots = SectionQueryService.get_section_slots(str(s_id))
                for ns in new_slots:
                    for es in slots:
                        if ns.day_of_week == es.day_of_week:
                            if _time_overlap(ns.start_time, ns.end_time, es.start_time, es.end_time):
                                raise BusinessRuleViolation("SCHEDULE_CONFLICT", "Schedule conflict with an existing section")

            # reserve seat (row lock in section module)
            SeatReservationService.reserve_seat(section_id)

            # create enrollment (unique constraint)
            enr = Enrollment.objects.create(
                student=student,
                section_id=section_id,
                term_id=sec.term_id,
                course_id=sec.course_id,
                status=Enrollment.STATUS_ACTIVE,
                source=Enrollment.SOURCE_NORMAL,
            )

            AuditService.log(
                actor=student,
                action="ENROLLMENT_CREATE",
                entity_type="Enrollment",
                entity_id=str(enr.id),
                after={"student_id": str(student.id), "section_id": str(section_id)},
                correlation_id=correlation_id,
            )

            OutboxEvent.objects.create(
                event_type=EnrollmentService.EVENT_ENROLLMENT_CREATED,
                version=1,
                correlation_id=correlation_id,
                payload={"student_id": str(student.id), "section_id": str(section_id), "term_id": str(sec.term_id), "course_id": str(sec.course_id)},
            )

            result = {"id": str(enr.id), "section_id": str(section_id), "status": enr.status, "source": enr.source}
            EnrollmentAttempt.objects.filter(idempotency_key=idempotency_key).update(result=result)
            return result

    @staticmethod
    def cancel(*, student, enrollment_id: str, correlation_id: str):
        with transaction.atomic():
            enr = Enrollment.objects.select_for_update().get(id=enrollment_id, student=student)
            if enr.status != Enrollment.STATUS_ACTIVE:
                raise BusinessRuleViolation("INVALID_STATUS", "Enrollment is not active")
            enr.status = Enrollment.STATUS_CANCELED
            enr.canceled_at = _now()
            enr.save(update_fields=["status","canceled_at"])

            # release seat in section module
            SeatReservationService.release_seat(str(enr.section_id))

            AuditService.log(
                actor=student,
                action="ENROLLMENT_CANCEL",
                entity_type="Enrollment",
                entity_id=str(enr.id),
                before={"status": "ACTIVE"},
                after={"status": "CANCELED"},
                correlation_id=correlation_id,
            )

            OutboxEvent.objects.create(
                event_type=EnrollmentService.EVENT_ENROLLMENT_CANCELLED,
                version=1,
                correlation_id=correlation_id,
                payload={"enrollment_id": str(enr.id), "student_id": str(student.id), "section_id": str(enr.section_id), "term_id": str(enr.term_id)},
            )
            return {"id": str(enr.id), "status": enr.status}

class EnrollmentOverrideService:
    @staticmethod
    def override_enroll(*, approver, student_id: str, section_id: str, reason: str, idempotency_key: str, correlation_id: str):
        if not reason:
            raise BusinessRuleViolation("REASON_REQUIRED", "Reason is required for override")
        # reuse EnrollmentService.enroll but mark source override and store decision
        attempt = EnrollmentAttempt.objects.filter(idempotency_key=idempotency_key).first()
        if attempt:
            return attempt.result

        with transaction.atomic():
            EnrollmentAttempt.objects.create(idempotency_key=idempotency_key, student_id=student_id, section_id=section_id, result={})
            sec = SectionQueryService.get_section_info(section_id)
            term = TermQueryService.get_status(sec.term_id)
            if term.status != "OPEN":
                raise ConflictError("TERM_LOCKED", "Term is not open for enrollment")

            # still enforce quota
            SeatReservationService.reserve_seat(section_id)

            # Create override decision
            OverrideDecision.objects.create(
                student_id=student_id,
                section_id=section_id,
                bypass_flags={"prereq": True, "conflict": True},
                reason=reason,
                approver=approver,
            )

            enr = Enrollment.objects.create(
                student_id=student_id,
                section_id=section_id,
                term_id=sec.term_id,
                course_id=sec.course_id,
                status=Enrollment.STATUS_ACTIVE,
                source=Enrollment.SOURCE_OVERRIDE,
                reason=reason,
            )

            AuditService.log(
                actor=approver,
                action="ENROLLMENT_OVERRIDE",
                entity_type="Enrollment",
                entity_id=str(enr.id),
                after={"student_id": str(student_id), "section_id": str(section_id), "reason": reason},
                correlation_id=correlation_id,
            )

            OutboxEvent.objects.create(
                event_type=EnrollmentService.EVENT_ENROLLMENT_CREATED,
                version=1,
                correlation_id=correlation_id,
                payload={"student_id": str(student_id), "section_id": str(section_id), "term_id": str(sec.term_id), "course_id": str(sec.course_id), "source": "OVERRIDE"},
            )
            result = {"id": str(enr.id), "section_id": str(section_id), "status": enr.status, "source": enr.source}
            EnrollmentAttempt.objects.filter(idempotency_key=idempotency_key).update(result=result)
            return result
