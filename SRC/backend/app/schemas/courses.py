import uuid
from pydantic import BaseModel, Field

class CourseCreate(BaseModel):
    course_code: str = Field(min_length=2, max_length=50)
    name_vi: str
    name_en: str
    credits: int = Field(ge=1, le=30)
    unit_id: uuid.UUID

class CourseVersionCreate(BaseModel):
    syllabus_text_vi: str | None = None
    syllabus_text_en: str | None = None
