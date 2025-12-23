import csv
from io import StringIO
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Student, Enrollment
from app.services.audit_service import write_audit

async def import_students_csv(db: AsyncSession, actor_id: uuid.UUID, program_id: uuid.UUID, csv_text: str) -> dict:
    f = StringIO(csv_text)
    reader = csv.DictReader(f)
    ok_count, fail = 0, []

    for idx, row in enumerate(reader, start=2):
        code = (row.get("student_code") or "").strip()
        name = (row.get("full_name") or "").strip()
        email = (row.get("email") or "").strip() or None
        if not code or not name:
            fail.append({"line": idx, "error": "Thiếu student_code hoặc full_name"})
            continue

        existed = (await db.execute(select(Student).where(Student.student_code == code))).scalars().first()
        if existed:
            fail.append({"line": idx, "error": f"Trùng mã SV: {code}"})
            continue

        db.add(Student(student_code=code, full_name=name, email=email, program_id=program_id, status="ACTIVE"))
        ok_count += 1

    await db.commit()
    await write_audit(db, actor_id=actor_id, action="IMPORT_STUDENTS", object_type="Program", object_id=program_id,
                      after_data={"ok": ok_count, "fail": len(fail)})
    return {"ok": ok_count, "fail": fail}

async def replace_enrollments(db: AsyncSession, actor_id: uuid.UUID, class_id: uuid.UUID, student_ids: list[uuid.UUID]) -> None:
    await db.execute(Enrollment.__table__.delete().where(Enrollment.class_id == class_id))
    for sid in student_ids:
        db.add(Enrollment(class_id=class_id, student_id=sid))
    await db.commit()
    await write_audit(db, actor_id=actor_id, action="UPDATE_ENROLLMENTS", object_type="Class", object_id=class_id,
                      after_data={"count": len(student_ids)})
