from fastapi import FastAPI

import app.models  # noqa: F401
from app.api import api_router
from app.core.config import settings
from app.db.migrations import ensure_student_access_codes
from app.db.session import Base, engine


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Taekwondo attendance system powered by FastAPI and LINE Messaging API.",
    )

    @app.on_event("startup")
    def on_startup() -> None:
        Base.metadata.create_all(bind=engine)
        ensure_student_access_codes(engine)

    @app.get("/")
    def root() -> dict[str, str]:
        return {"message": f"{settings.PROJECT_NAME} is running"}

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(api_router)
    return app


app = create_app()
