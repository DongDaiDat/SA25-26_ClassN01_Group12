import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import require_perm
from app.schemas.common import ok
from app.schemas.sis import StudentCreate, ClassCreate, EnrollmentUpdate
from app.db.models import Student, ClassEntity
from app.services.sis_service import import_students_csv, replace_enrollments

router = APIRouter()

@router.post("/students")
async def create_student(payload: StudentCreate, db: AsyncSession = Depends(get_db), user=Depends(require_perm("SIS_MANAGE"))):
    s = Student(**payload.model_dump())
    db.add(s)
    await db.commit()
    return ok({"student_id": str(s.student_id)})

@router.post("/students/import")
async def import_students(program_id: uuid.UUID, file: UploadFile = File(...), db: AsyncSession = Depends(get_db), user=Depends(require_perm("SIS_MANAGE"))):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="ONLY_CSV_FOR_MVP")
    text = (await file.read()).decode("utf-8", errors="ignore")
    res = await import_students_csv(db, user.user_id, program_id, text)
    return ok(res)

@router.post("/classes")
async def create_class(payload: ClassCreate, db: AsyncSession = Depends(get_db), user=Depends(require_perm("SIS_MANAGE"))):
    c = ClassEntity(**payload.model_dump())
    db.add(c)
    await db.commit()
    return ok({"class_id": str(c.class_id)})

@router.put("/classes/{class_id}/enrollments")
async def update_enrollments(class_id: uuid.UUID, payload: EnrollmentUpdate, db: AsyncSession = Depends(get_db), user=Depends(require_perm("SIS_MANAGE"))):
    await replace_enrollments(db, user.user_id, class_id, payload.student_ids)
    return ok({"updated": True, "count": len(payload.student_ids)})
