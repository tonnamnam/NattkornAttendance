from fastapi import Header, HTTPException, status

from app.core.config import settings


def require_admin(x_api_key: str | None = Header(default=None)) -> None:
    if not settings.ADMIN_API_KEY:
        return
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin API key.")
