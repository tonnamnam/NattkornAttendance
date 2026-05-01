from fastapi import APIRouter

from app.routers import accounts, admin, classes, line, report, students


api_router = APIRouter()
api_router.include_router(line.router, prefix="/line", tags=["LINE"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(classes.router, prefix="/classes", tags=["Classes"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(report.router, prefix="/report", tags=["Reports"])
