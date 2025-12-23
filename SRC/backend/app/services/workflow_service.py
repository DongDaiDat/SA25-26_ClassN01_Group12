import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import ApprovalWorkflow, WorkflowStep, ChangeRequest, Approval
from app.services.audit_service import write_audit

async def get_workflow(db: AsyncSession, code: str) -> ApprovalWorkflow:
    wf = (await db.execute(select(ApprovalWorkflow).where(
        ApprovalWorkflow.workflow_code == code,
        ApprovalWorkflow.is_active == True
    ))).scalars().first()  # noqa
    if not wf:
        raise ValueError("WORKFLOW_NOT_FOUND")
    return wf

async def start_cr(db: AsyncSession, actor_id: uuid.UUID, workflow_code: str, target_type: str, target_id: uuid.UUID,
                   title: str, description: str | None, payload: dict) -> ChangeRequest:
    wf = await get_workflow(db, workflow_code)
    cr = ChangeRequest(
        workflow_id=wf.workflow_id,
        target_type=target_type,
        target_id=target_id,
        title=title,
        description=description,
        payload_json=payload,
        state="PENDING",
        current_step_no=1,
        created_by=actor_id,
    )
    db.add(cr)
    await db.commit()

    steps = (await db.execute(select(WorkflowStep).where(WorkflowStep.workflow_id == wf.workflow_id).order_by(WorkflowStep.step_no))).scalars().all()
    for s in steps:
        db.add(Approval(cr_id=cr.cr_id, step_no=s.step_no))
    await db.commit()

    await write_audit(db, actor_id=actor_id, action="CREATE_CR", object_type="ChangeRequest", object_id=cr.cr_id,
                      after_data={"workflow_code": workflow_code})
    return cr

async def decide(db: AsyncSession, actor_id: uuid.UUID, cr_id: uuid.UUID, step_no: int, decision: str, comment: str | None) -> ChangeRequest:
    cr = (await db.execute(select(ChangeRequest).where(ChangeRequest.cr_id == cr_id))).scalars().first()
    if not cr:
        raise ValueError("CR_NOT_FOUND")
    if cr.current_step_no != step_no:
        raise ValueError("STEP_MISMATCH")

    step = (await db.execute(select(WorkflowStep).where(
        WorkflowStep.workflow_id == cr.workflow_id,
        WorkflowStep.step_no == cr.current_step_no
    ))).scalars().first()
    if not step:
        raise ValueError("WORKFLOW_STEP_NOT_FOUND")

    ap = (await db.execute(select(Approval).where(Approval.cr_id == cr_id, Approval.step_no == step_no))).scalars().first()
    if not ap:
        raise ValueError("APPROVAL_ROW_NOT_FOUND")

    ap.decision = decision
    ap.comment = comment
    ap.decided_by = actor_id
    ap.decided_at = datetime.now(timezone.utc)

    if decision == "NEED_MORE_INFO":
        if not step.allow_request_more_info:
            raise ValueError("MORE_INFO_NOT_ALLOWED")
        cr.state = "NEED_MORE_INFO"
    elif decision == "REJECT":
        cr.state = "REJECTED"
    elif decision == "APPROVE":
        next_step = (await db.execute(select(WorkflowStep).where(
            WorkflowStep.workflow_id == cr.workflow_id,
            WorkflowStep.step_no == step_no + 1
        ))).scalars().first()
        if next_step:
            cr.current_step_no = step_no + 1
            cr.state = "PENDING"
        else:
            cr.state = "APPROVED"
    else:
        raise ValueError("DECISION_INVALID")

    await db.commit()
    await write_audit(db, actor_id=actor_id, action=f"CR_{decision}", object_type="ChangeRequest", object_id=cr_id,
                      after_data={"step_no": step_no})
    return cr

async def resubmit(db: AsyncSession, actor_id: uuid.UUID, cr_id: uuid.UUID, payload_patch: dict) -> ChangeRequest:
    cr = (await db.execute(select(ChangeRequest).where(ChangeRequest.cr_id == cr_id))).scalars().first()
    if not cr:
        raise ValueError("CR_NOT_FOUND")
    if cr.state != "NEED_MORE_INFO":
        raise ValueError("CR_NOT_IN_MORE_INFO")

    new_payload = dict(cr.payload_json)
    new_payload.update(payload_patch)
    cr.payload_json = new_payload
    cr.state = "PENDING"
    await db.commit()

    await write_audit(db, actor_id=actor_id, action="CR_RESUBMIT", object_type="ChangeRequest", object_id=cr_id)
    return cr
