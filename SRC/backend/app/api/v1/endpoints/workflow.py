import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.api.deps import get_current_user, require_perm
from app.schemas.common import ok
from app.schemas.workflow import ChangeRequestCreate, DecisionIn
from app.services import workflow_service
from app.db.models import ChangeRequest

router = APIRouter()

@router.post("")
async def create_cr(payload: ChangeRequestCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    cr = await workflow_service.start_cr(
        db, user.user_id,
        payload.workflow_code,
        payload.target_type,
        payload.target_id,
        payload.title,
        payload.description,
        payload.payload
    )
    return ok({"cr_id": str(cr.cr_id), "state": cr.state, "current_step_no": cr.current_step_no})

@router.get("/{cr_id}")
async def get_cr(cr_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    cr = (await db.execute(select(ChangeRequest).where(ChangeRequest.cr_id == cr_id))).scalars().first()
    if not cr:
        raise HTTPException(status_code=404, detail="CR_NOT_FOUND")
    return ok({
        "cr_id": str(cr.cr_id),
        "workflow_id": str(cr.workflow_id),
        "target_type": cr.target_type,
        "target_id": str(cr.target_id),
        "title": cr.title,
        "description": cr.description,
        "state": cr.state,
        "current_step_no": cr.current_step_no,
        "payload": cr.payload_json,
    })

@router.post("/{cr_id}/approve")
async def approve(cr_id: uuid.UUID, payload: DecisionIn, db: AsyncSession = Depends(get_db), user=Depends(require_perm("WORKFLOW_APPROVE"))):
    cr = await workflow_service.decide(db, user.user_id, cr_id, payload.step_no, "APPROVE", payload.comment)
    return ok({"state": cr.state, "current_step_no": cr.current_step_no})

@router.post("/{cr_id}/need-more-info")
async def need_more_info(cr_id: uuid.UUID, payload: DecisionIn, db: AsyncSession = Depends(get_db), user=Depends(require_perm("WORKFLOW_APPROVE"))):
    cr = await workflow_service.decide(db, user.user_id, cr_id, payload.step_no, "NEED_MORE_INFO", payload.comment)
    return ok({"state": cr.state, "current_step_no": cr.current_step_no})

@router.post("/{cr_id}/reject")
async def reject(cr_id: uuid.UUID, payload: DecisionIn, db: AsyncSession = Depends(get_db), user=Depends(require_perm("WORKFLOW_APPROVE"))):
    cr = await workflow_service.decide(db, user.user_id, cr_id, payload.step_no, "REJECT", payload.comment)
    return ok({"state": cr.state, "current_step_no": cr.current_step_no})

@router.post("/{cr_id}/resubmit")
async def resubmit(cr_id: uuid.UUID, payload: dict, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        cr = await workflow_service.resubmit(db, user.user_id, cr_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ok({"state": cr.state, "current_step_no": cr.current_step_no})
