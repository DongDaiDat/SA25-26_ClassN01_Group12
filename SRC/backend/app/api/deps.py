import uuid
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import decode_token
from app.core.rbac import PERM
from app.db.session import get_db
from app.db.models import User, UserRole, Role as RoleModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    try:
        payload = decode_token(token, settings.secret_key)
    except Exception:
        raise HTTPException(status_code=401, detail="TOKEN_INVALID")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="TOKEN_INVALID_TYPE")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="TOKEN_NO_SUB")

    user = (await db.execute(select(User).where(User.user_id == uuid.UUID(user_id), User.is_deleted == False))).scalars().first()  # noqa
    if not user:
        raise HTTPException(status_code=401, detail="USER_NOT_FOUND")
    if user.status != "ACTIVE":
        raise HTTPException(status_code=423, detail="USER_INACTIVE")
    return user

async def get_user_roles(db: AsyncSession, user_id: uuid.UUID) -> set[str]:
    rows = (await db.execute(
        select(RoleModel.role_name)
        .join(UserRole, RoleModel.role_id == UserRole.role_id)
        .where(UserRole.user_id == user_id)
    )).scalars().all()
    return set(rows)

def require_perm(perm_name: str):
    async def _dep(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> User:
        roles = await get_user_roles(db, user.user_id)
        allowed = {r.value for r in PERM.get(perm_name, set())}
        if not roles.intersection(allowed):
            raise HTTPException(status_code=403, detail="FORBIDDEN")
        return user
    return _dep
