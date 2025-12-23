import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from app.db.models import Program, ProgramVersion, CurriculumItem
from app.services.audit_service import write_audit

async def list_programs(db: AsyncSession) -> list[Program]:
    return list((await db.execute(select(Program).where(Program.is_deleted == False))).scalars().all())  # noqa

async def create_program(db: AsyncSession, actor_id: uuid.UUID, p: Program) -> Program:
    db.add(p)
    await db.commit()
    await write_audit(db, actor_id=actor_id, action="CREATE", object_type="Program", object_id=p.program_id,
                      after_data={"program_code": p.program_code})
    return p

async def create_program_version(db: AsyncSession, actor_id: uuid.UUID, program_id: uuid.UUID, apply_year: int, copy_from_latest: bool=True) -> ProgramVersion:
    latest_no = (await db.execute(select(func.max(ProgramVersion.version_no)).where(ProgramVersion.program_id == program_id))).scalar() or 0
    pv = ProgramVersion(program_id=program_id, version_no=latest_no+1, apply_year=apply_year, state="DRAFT", created_by=actor_id)
    db.add(pv)
    await db.commit()

    if copy_from_latest and latest_no > 0:
        latest = (await db.execute(select(ProgramVersion).where(ProgramVersion.program_id==program_id, ProgramVersion.version_no==latest_no))).scalars().first()
        if latest:
            items = (await db.execute(select(CurriculumItem).where(CurriculumItem.program_version_id == latest.program_version_id))).scalars().all()
            for it in items:
                db.add(CurriculumItem(
                    program_version_id=pv.program_version_id,
                    course_version_id=it.course_version_id,
                    semester_no=it.semester_no,
                    course_type=it.course_type,
                    note=it.note,
                ))
            await db.commit()

    await write_audit(db, actor_id=actor_id, action="CREATE_VERSION", object_type="ProgramVersion", object_id=pv.program_version_id,
                      after_data={"apply_year": apply_year})
    return pv

async def replace_curriculum(db: AsyncSession, actor_id: uuid.UUID, program_version_id: uuid.UUID, items: list[dict]) -> None:
    await db.execute(delete(CurriculumItem).where(CurriculumItem.program_version_id == program_version_id))
    for it in items:
        db.add(CurriculumItem(program_version_id=program_version_id, **it))
    await db.commit()
    await write_audit(db, actor_id=actor_id, action="UPDATE_CURRICULUM", object_type="ProgramVersion", object_id=program_version_id,
                      after_data={"count": len(items)})
