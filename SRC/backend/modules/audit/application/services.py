from typing import Optional, Any, Dict
from django.contrib.auth import get_user_model
from modules.audit.infrastructure.models import AuditLog

User = get_user_model()

class AuditService:
    @staticmethod
    def log(
        *,
        actor: Optional[User],
        action: str,
        entity_type: str = "",
        entity_id: str = "",
        result: str = "SUCCESS",
        reason_code: str = "",
        before: Optional[Dict[str, Any]] = None,
        after: Optional[Dict[str, Any]] = None,
        correlation_id: str = "",
        ip: str = "",
        user_agent: str = "",
    ) -> AuditLog:
        return AuditLog.objects.create(
            actor=actor,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else "",
            result=result,
            reason_code=reason_code,
            before=before,
            after=after,
            correlation_id=correlation_id,
            ip=ip or None,
            user_agent=user_agent or "",
        )
