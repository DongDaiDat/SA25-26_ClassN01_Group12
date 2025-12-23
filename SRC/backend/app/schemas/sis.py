import uuid
from pydantic import BaseModel, Field, EmailStr

class StudentCreate(BaseModel):
    student_code: str
    full_name: str
    email: EmailStr | None = None
    program_id: uuid.UUID
    status: str = "ACTIVE"

class ClassCreate(BaseModel):
    class_code: str
    name: str
    class_type: str = Field(pattern="^(ADMIN|SECTION)$")
    program_id: uuid.UUID
    course_version_id: uuid.UUID | None = None
    academic_year: str
    semester: int = Field(ge=1, le=3)

class EnrollmentUpdate(BaseModel):
    student_ids: list[uuid.UUID]
