import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import Course, CourseVersion
from app.services.audit_service import write_audit

async def list_courses(db: AsyncSession) -> list[Course]:
    return list((await db.execute(select(Course))).scalars().all())

async def create_course(db: AsyncSession, actor_id: uuid.UUID, c: Course) -> Course:
    db.add(c)
    await db.commit()
    await write_audit(db, actor_id=actor_id, action="CREATE", object_type="Course", object_id=c.course_id,
                      after_data={"course_code": c.course_code})
    return c

async def create_course_version(db: AsyncSession, actor_id: uuid.UUID, course_id: uuid.UUID, vi: str | None, en: str | None) -> CourseVersion:
    latest_no = (await db.execute(select(func.max(CourseVersion.version_no)).where(CourseVersion.course_id == course_id))).scalar() or 0
    cv = CourseVersion(
        course_id=course_id,
        version_no=latest_no+1,
        state="DRAFT",
        is_published=False,
        syllabus_text_vi=vi,
        syllabus_text_en=en,
        owner_id=actor_id,
    )
    db.add(cv)
    await db.commit()
    await write_audit(db, actor_id=actor_id, action="CREATE_VERSION", object_type="CourseVersion", object_id=cv.course_version_id,
                      after_data={"course_id": str(course_id)})
    return cv
