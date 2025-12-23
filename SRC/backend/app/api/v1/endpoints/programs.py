import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import require_perm
from app.schemas.common import ok
from app.schemas.programs import ProgramCreate, ProgramVersionCreate, CurriculumUpdate
from app.db.models import Program
from app.services import program_service

router = APIRouter()

@router.get("")
async def list_programs(db: AsyncSession = Depends(get_db), user=Depends(require_perm("PROGRAM_VIEW"))):
    programs = await program_service.list_programs(db)
    data = [{
        "program_id": str(p.program_id),
        "program_code": p.program_code,
        "name_vi": p.name_vi,
        "name_en": p.name_en,
        "level": p.level,
        "unit_id": str(p.unit_id),
    } for p in programs]
    return ok(data)

@router.post("")
async def create_program(payload: ProgramCreate, db: AsyncSession = Depends(get_db), user=Depends(require_perm("PROGRAM_CREATE"))):
    p = Program(**payload.model_dump())
    p = await program_service.create_program(db, user.user_id, p)
    return ok({"program_id": str(p.program_id)})

@router.post("/{program_id}/versions")
async def create_version(program_id: uuid.UUID, payload: ProgramVersionCreate, db: AsyncSession = Depends(get_db), user=Depends(require_perm("PROGRAM_CREATE"))):
    pv = await program_service.create_program_version(db, user.user_id, program_id, payload.apply_year, payload.copy_from_latest)
    return ok({"program_version_id": str(pv.program_version_id), "version_no": pv.version_no, "apply_year": pv.apply_year, "state": pv.state})

@router.put("/versions/{program_version_id}/curriculum-items")
async def replace_curriculum(program_version_id: uuid.UUID, payload: CurriculumUpdate, db: AsyncSession = Depends(get_db), user=Depends(require_perm("PROGRAM_CREATE"))):
    items = [i.model_dump() for i in payload.items]
    await program_service.replace_curriculum(db, user.user_id, program_version_id, items)
    return ok({"updated": True, "count": len(items)})
