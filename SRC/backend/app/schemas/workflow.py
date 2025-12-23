import uuid
from pydantic import BaseModel

class ChangeRequestCreate(BaseModel):
    workflow_code: str
    target_type: str
    target_id: uuid.UUID
    title: str
    description: str | None = None
    payload: dict

class DecisionIn(BaseModel):
    step_no: int
    comment: str | None = None

