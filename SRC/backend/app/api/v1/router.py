from fastapi import APIRouter
from app.api.v1.endpoints import auth, programs, courses, workflow, reports, sis, audit, files

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(programs.router, prefix="/programs", tags=["programs"])
router.include_router(courses.router, prefix="/courses", tags=["courses"])
router.include_router(workflow.router, prefix="/change-requests", tags=["workflow"])
router.include_router(reports.router, prefix="/reports", tags=["reports"])
router.include_router(sis.router, prefix="/sis", tags=["sis"])
router.include_router(audit.router, prefix="/audit-logs", tags=["audit"])
router.include_router(files.router, prefix="/files", tags=["files"])
