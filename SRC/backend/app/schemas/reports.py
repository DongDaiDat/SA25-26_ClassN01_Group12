import uuid
from pydantic import BaseModel

class ExportMOETRequest(BaseModel):
    program_version_id: uuid.UUID
    template_code: str
