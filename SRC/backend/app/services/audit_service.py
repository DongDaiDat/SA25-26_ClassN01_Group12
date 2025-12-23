import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AuditLog

async def write_audit(
    db: AsyncSession,
    *,
    actor_id: uuid.UUID,
    action: str,
    object_type: str,
    object_id: uuid.UUID,
    before_data: dict | None = None,
    after_data: dict | None = None,
) -> None:
    db.add(AuditLog(
        actor_id=actor_id,
        action=action,
        object_type=object_type,
        object_id=object_id,
        before_data=before_data,
        after_data=after_data,
    ))
    await db.commit()
