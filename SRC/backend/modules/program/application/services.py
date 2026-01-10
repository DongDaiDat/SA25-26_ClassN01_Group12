from django.db import transaction
from modules.program.infrastructure.models import CurriculumVersion
from modules.shared.exceptions import BusinessRuleViolation
from modules.audit.application.services import AuditService

class CurriculumService:
    @staticmethod
    @transaction.atomic
    def publish(curriculum_id, *, actor, correlation_id=""):
        cv = CurriculumVersion.objects.select_for_update().get(id=curriculum_id)
        if cv.status != CurriculumVersion.STATUS_DRAFT:
            raise BusinessRuleViolation("INVALID_STATUS", "Only draft curriculum can be published")
        # minimal validation: must have at least 1 node
        if cv.nodes.count() == 0:
            raise BusinessRuleViolation("EMPTY_STRUCTURE", "Curriculum structure is empty")
        before = {"status": cv.status}
        cv.status = CurriculumVersion.STATUS_PUBLISHED
        cv.save(update_fields=["status"])
        AuditService.log(actor=actor, action="CURRICULUM_PUBLISH", entity_type="CurriculumVersion", entity_id=str(cv.id),
                         before=before, after={"status": cv.status}, correlation_id=correlation_id)
        return cv
