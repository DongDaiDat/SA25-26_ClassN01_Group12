from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.api.deps import require_perm
from app.schemas.common import ok
from app.db.models import AuditLog

router = APIRouter()

@router.get("")
async def list_audit(db: AsyncSession = Depends(get_db), user=Depends(require_perm("AUDIT_VIEW"))):
    rows = (await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200))).scalars().all()
    return ok([{
        "log_id": str(r.log_id),
        "actor_id": str(r.actor_id),
        "action": r.action,
        "object_type": r.object_type,
        "object_id": str(r.object_id),
        "created_at": r.created_at.isoformat() if r.created_at else None
    } for r in rows])
