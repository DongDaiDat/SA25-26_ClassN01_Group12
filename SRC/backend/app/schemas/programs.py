import uuid
from pydantic import BaseModel, Field

class ProgramCreate(BaseModel):
    program_code: str = Field(min_length=2, max_length=50)
    name_vi: str
    name_en: str
    level: str
    unit_id: uuid.UUID

class ProgramVersionCreate(BaseModel):
    apply_year: int
    copy_from_latest: bool = True

class CurriculumItemIn(BaseModel):
    course_version_id: uuid.UUID
    semester_no: int
    course_type: str
    note: str | None = None

class CurriculumUpdate(BaseModel):
    items: list[CurriculumItemIn]
