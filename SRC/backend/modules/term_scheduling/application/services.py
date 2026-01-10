from dataclasses import dataclass
from modules.term_scheduling.infrastructure.models import Term
from modules.shared.exceptions import BusinessRuleViolation
from modules.audit.application.services import AuditService

@dataclass(frozen=True)
class TermStatusDTO:
    term_id: str
    status: str
    enroll_open_at: str
    enroll_close_at: str

class TermQueryService:
    @staticmethod
    def get(term_id: str) -> Term:
        return Term.objects.get(id=term_id)

    @staticmethod
    def get_status(term_id: str) -> TermStatusDTO:
        t = TermQueryService.get(term_id)
        return TermStatusDTO(str(t.id), t.status, t.enroll_open_at.isoformat(), t.enroll_close_at.isoformat())

class TermCommandService:
    @staticmethod
    def set_status(term_id: str, status: str, *, actor, correlation_id=""):
        t = Term.objects.get(id=term_id)
        allowed = {Term.STATUS_DRAFT, Term.STATUS_OPEN, Term.STATUS_LOCKED, Term.STATUS_CLOSED}
        if status not in allowed:
            raise BusinessRuleViolation("INVALID_STATUS", "Invalid term status")
        before = {"status": t.status}
        t.status = status
        t.save(update_fields=["status"])
        AuditService.log(actor=actor, action="TERM_SET_STATUS", entity_type="Term", entity_id=str(t.id),
                         before=before, after={"status": t.status}, correlation_id=correlation_id)
        return t
