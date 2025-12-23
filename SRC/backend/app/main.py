from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
from app.api.v1.router import router as api_router
from app.services.auth_service import seed_admin
from app.services.seed import seed_workflows

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # DEV: tự tạo bảng để chạy nhanh. Production: dùng Alembic.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        await seed_admin(db)
        await seed_workflows(db)

app.include_router(api_router, prefix=settings.api_prefix)

@app.get("/health")
async def health():
    return {"ok": True}
