import secrets
from django.db import transaction
from modules.certificate.infrastructure.models import CertificateDefinition, CertificateIssue
from modules.assessment.application.services import AssessmentQueryService
from modules.shared.exceptions import BusinessRuleViolation
from modules.audit.application.services import AuditService
from modules.shared.models import OutboxEvent

class CertificateService:
    @staticmethod
    def _new_verify_code():
        return secrets.token_hex(5).upper()

    @staticmethod
    @transaction.atomic
    def issue(*, actor, definition_id: str, student_id: str, correlation_id: str):
        definition = CertificateDefinition.objects.get(id=definition_id)
        rules = definition.rules or {}
        required_courses = [str(x) for x in rules.get("required_course_ids", [])]
        min_grade = rules.get("min_grade", 5.0)

        missing = []
        for cid in required_courses:
            if not AssessmentQueryService.has_passed_course(student_id=str(student_id), course_id=cid, min_grade=min_grade):
                missing.append(cid)
        if missing:
            raise BusinessRuleViolation("CERT_CONDITION_NOT_MET", "Student does not meet certificate conditions", details={"missing_course_ids": missing})

        # unique verify code
        verify_code = CertificateService._new_verify_code()
        while CertificateIssue.objects.filter(verify_code=verify_code).exists():
            verify_code = CertificateService._new_verify_code()

        issue = CertificateIssue.objects.create(
            definition=definition,
            student_id=student_id,
            issued_by=actor,
            verify_code=verify_code,
            metadata={"min_grade": min_grade, "required_course_ids": required_courses},
        )
        AuditService.log(actor=actor, action="CERTIFICATE_ISSUE", entity_type="CertificateIssue", entity_id=str(issue.id),
                         after={"student_id": str(student_id), "definition_code": definition.code, "verify_code": verify_code}, correlation_id=correlation_id)

        OutboxEvent.objects.create(
            event_type="CertificateIssued",
            version=1,
            correlation_id=correlation_id,
            payload={"certificate_issue_id": str(issue.id), "student_id": str(student_id), "definition_code": definition.code, "verify_code": verify_code},
        )
        return issue
