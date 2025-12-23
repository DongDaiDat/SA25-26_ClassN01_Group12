import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import require_perm
from app.schemas.common import ok
from app.schemas.courses import CourseCreate, CourseVersionCreate
from app.db.models import Course
from app.services import course_service

router = APIRouter()

@router.get("")
async def list_courses(db: AsyncSession = Depends(get_db), user=Depends(require_perm("PROGRAM_VIEW"))):
    courses = await course_service.list_courses(db)
    data = [{
        "course_id": str(c.course_id),
        "course_code": c.course_code,
        "name_vi": c.name_vi,
        "name_en": c.name_en,
        "credits": c.credits,
        "unit_id": str(c.unit_id),
    } for c in courses]
    return ok(data)

@router.post("")
async def create_course(payload: CourseCreate, db: AsyncSession = Depends(get_db), user=Depends(require_perm("COURSE_MANAGE"))):
    c = Course(**payload.model_dump())
    c = await course_service.create_course(db, user.user_id, c)
    return ok({"course_id": str(c.course_id)})

@router.post("/{course_id}/versions")
async def create_course_version(course_id: uuid.UUID, payload: CourseVersionCreate, db: AsyncSession = Depends(get_db), user=Depends(require_perm("SYLLABUS_EDIT"))):
    cv = await course_service.create_course_version(db, user.user_id, course_id, payload.syllabus_text_vi, payload.syllabus_text_en)
    return ok({"course_version_id": str(cv.course_version_id), "version_no": cv.version_no, "state": cv.state})
