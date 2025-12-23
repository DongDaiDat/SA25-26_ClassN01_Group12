from typing import Any, Optional
from pydantic import BaseModel

class ApiError(BaseModel):
    code: str
    message: str
    details: Optional[dict[str, Any]] = None

def ok(data: Any = None, meta: Optional[dict] = None) -> dict:
    return {"success": True, "data": data, "meta": meta}

def fail(code: str, message: str, details: Optional[dict] = None) -> dict:
    return {"success": False, "error": {"code": code, "message": message, "details": details}}
