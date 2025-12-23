import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles

from app.db.session import get_db
from app.api.deps import require_perm
from app.schemas.common import ok
from app.schemas.reports import ExportMOETRequest
from app.services.report_service import export_moet, upload_template

router = APIRouter()

@router.post("/templates/upload")
async def upload_template_endpoint(
    template_code: str = Form(...),
    name: str = Form(...),
    version: int = Form(1),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_perm("REPORT_EXPORT"))
):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="ONLY_DOCX_TEMPLATE_SUPPORTED")

    save_dir = "/data/files"
    os.makedirs(save_dir, exist_ok=True)
    file_tag = uuid.uuid4().hex
    storage_path = os.path.join(save_dir, f"tpl_{template_code}_{file_tag}.docx")

    async with aiofiles.open(storage_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    try:
        res = await upload_template(
            db, user.user_id,
            template_code=template_code,
            name=name,
            version=version,
            storage_path=storage_path,
            file_name=file.filename,
            mime_type=file.content_type or "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            size=len(content),
        )
        return ok(res)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/moet/export")
async def export_moet_endpoint(payload: ExportMOETRequest, db: AsyncSession = Depends(get_db), user=Depends(require_perm("REPORT_EXPORT"))):
    try:
        res = await export_moet(db, user.user_id, payload.program_version_id, payload.template_code)
        return ok(res)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
