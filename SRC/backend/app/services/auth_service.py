import uuid
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_token
from app.db.models import User, Role, UserRole, OrgUnit

# MVP token store in-memory (demo). Production: lưu DB + expire.
_verify_tokens: dict[str, str] = {}
_reset_tokens: dict[str, str] = {}

async def authenticate(db: AsyncSession, email: str, password: str) -> User | None:
    user = (await db.execute(select(User).where(User.email == email, User.is_deleted == False))).scalars().first()  # noqa
    if not user or user.status != "ACTIVE":
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def issue_access_token(user_id: str) -> str:
    return create_token(
        subject=user_id,
        secret_key=settings.secret_key,
        expires_delta=timedelta(minutes=60),
        token_type="access",
    )

def generate_verify_token(email: str) -> str:
    token = str(uuid.uuid4())
    _verify_tokens[token] = email
    return token

def consume_verify_token(token: str) -> str | None:
    return _verify_tokens.pop(token, None)

def generate_reset_token(email: str) -> str:
    token = str(uuid.uuid4())
    _reset_tokens[token] = email
    return token

def consume_reset_token(token: str) -> str | None:
    return _reset_tokens.pop(token, None)

async def seed_admin(db: AsyncSession) -> None:
    # 1) seed org unit UNI
    uni = (await db.execute(select(OrgUnit))).scalars().first()
    if not uni:
        uni = OrgUnit(unit_name="UNI", unit_type="UNI", parent_id=None, is_active=True)
        db.add(uni)
        await db.commit()

    # 2) seed roles
    if not (await db.execute(select(Role))).scalars().first():
        roles = [
            Role(role_id=1, role_name="ADMIN"),
            Role(role_id=2, role_name="TRAINING_OFFICE"),
            Role(role_id=3, role_name="FACULTY"),
            Role(role_id=4, role_name="QA"),
            Role(role_id=5, role_name="DEPT_HEAD"),
            Role(role_id=6, role_name="LECTURER"),
            Role(role_id=7, role_name="VIEWER"),
            Role(role_id=8, role_name="SIS_STAFF"),
        ]
        db.add_all(roles)
        await db.commit()

    # 3) seed admin user
    admin = (await db.execute(select(User).where(User.email == "admin@unimis.local"))).scalars().first()
    if not admin:
        admin = User(
            email="admin@unimis.local",
            password_hash=hash_password("Admin@123"),
            full_name="System Admin",
            primary_unit_id=uni.unit_id,
            email_verified=True,
            status="ACTIVE",
        )
        db.add(admin)
        await db.commit()
        db.add(UserRole(user_id=admin.user_id, role_id=1, scope_unit_id=None))
        await db.commit()
