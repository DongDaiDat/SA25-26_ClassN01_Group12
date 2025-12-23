from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.schemas.common import ok
from app.schemas.auth import LoginRequest, VerifyEmailRequest, VerifyEmailConfirm, ForgotPasswordRequest, ResetPasswordRequest
from app.services.auth_service import authenticate, issue_access_token, generate_verify_token, consume_verify_token, generate_reset_token, consume_reset_token
from app.utils.email import send_email
from app.db.models import User
from app.core.security import hash_password

router = APIRouter()

@router.post("/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="INVALID_CREDENTIALS")
    access = issue_access_token(str(user.user_id))
    return ok({"accessToken": access, "tokenType": "bearer"})

@router.post("/verify-email/request")
async def request_verify(payload: VerifyEmailRequest):
    token = generate_verify_token(payload.email)
    link = f"http://localhost:5173/verify-email?token={token}"
    html = f"<p>Nhấn link để xác thực email: <a href='{link}'>{link}</a></p>"
    try:
        await send_email(payload.email, "Xác thực email UniMIS", html)
        return ok({"sent": True})
    except Exception:
        return ok({"sent": False, "token_for_dev": token})

@router.post("/verify-email/confirm")
async def confirm_verify(payload: VerifyEmailConfirm, db: AsyncSession = Depends(get_db)):
    email = consume_verify_token(payload.token)
    if not email:
        raise HTTPException(status_code=400, detail="TOKEN_INVALID_OR_EXPIRED")
    u = (await db.execute(select(User).where(User.email == email))).scalars().first()
    if u:
        u.email_verified = True
        await db.commit()
    return ok({"verified": True})

@router.post("/password/forgot")
async def forgot(payload: ForgotPasswordRequest):
    token = generate_reset_token(payload.email)
    link = f"http://localhost:5173/reset-password?token={token}"
    html = f"<p>Đặt lại mật khẩu: <a href='{link}'>{link}</a></p>"
    try:
        await send_email(payload.email, "Đặt lại mật khẩu UniMIS", html)
        return ok({"sent": True})
    except Exception:
        return ok({"sent": False, "token_for_dev": token})

@router.post("/password/reset")
async def reset(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    email = consume_reset_token(payload.token)
    if not email:
        raise HTTPException(status_code=400, detail="TOKEN_INVALID_OR_EXPIRED")
    u = (await db.execute(select(User).where(User.email == email))).scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    u.password_hash = hash_password(payload.newPassword)
    await db.commit()
    return ok({"reset": True})
