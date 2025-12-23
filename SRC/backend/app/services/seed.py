from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import ApprovalWorkflow, WorkflowStep

ROLE_ID = {
    "ADMIN": 1,
    "TRAINING_OFFICE": 2,
    "FACULTY": 3,
    "QA": 4,
    "DEPT_HEAD": 5,
    "LECTURER": 6,
    "VIEWER": 7,
    "SIS_STAFF": 8,
}

DEFAULT_WORKFLOWS = [
    # Ví dụ đúng theo bạn chốt: tạo CTĐT mới: khoa -> phòng đào tạo (duyệt cuối)
    {"code": "PROGRAM_CREATE", "name": "Tạo CTĐT mới", "target_type": "PROGRAM",
     "steps": [("FACULTY", True), ("TRAINING_OFFICE", True)]},

    # Ban hành phiên bản: khoa -> QA -> phòng đào tạo
    {"code": "PROGRAM_PUBLISH", "name": "Ban hành phiên bản CTĐT", "target_type": "PROGRAM_VERSION",
     "steps": [("FACULTY", True), ("QA", True), ("TRAINING_OFFICE", True)]},

    # Công bố đề cương: trưởng bộ môn -> QA
    {"code": "SYLLABUS_PUBLISH", "name": "Công bố đề cương", "target_type": "COURSE_VERSION",
     "steps": [("DEPT_HEAD", True), ("QA", True)]},
]

async def seed_workflows(db: AsyncSession) -> None:
    for wf in DEFAULT_WORKFLOWS:
        existed = (await db.execute(select(ApprovalWorkflow).where(ApprovalWorkflow.workflow_code == wf["code"]))).scalars().first()
        if existed:
            continue
        aw = ApprovalWorkflow(workflow_code=wf["code"], name=wf["name"], target_type=wf["target_type"], is_active=True)
        db.add(aw)
        await db.commit()

        for idx, (role_name, allow_more) in enumerate(wf["steps"], start=1):
            db.add(WorkflowStep(
                workflow_id=aw.workflow_id,
                step_no=idx,
                approver_role_id=ROLE_ID[role_name],
                allow_request_more_info=allow_more,
            ))
        await db.commit()
