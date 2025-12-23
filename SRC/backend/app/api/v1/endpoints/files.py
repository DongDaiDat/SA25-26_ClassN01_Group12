from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

from app.db.session import get_db
from app.api.deps import get_current_user
from app.db.models import FileAsset

router = APIRouter()

@router.get("/{file_id}/download")
async def download_by_id(file_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    fa = (await db.execute(select(FileAsset).where(FileAsset.file_id == file_id))).scalars().first()
    if not fa:
        raise HTTPException(status_code=404, detail="FILE_NOT_FOUND")
    if not os.path.exists(fa.storage_path):
        raise HTTPException(status_code=404, detail="FILE_MISSING_ON_DISK")
    return FileResponse(fa.storage_path, filename=fa.file_name, media_type=fa.mime_type)
