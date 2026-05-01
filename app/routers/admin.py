from fastapi import APIRouter, Depends, status

from app.core.security import require_admin
from app.schemas.broadcast import BroadcastRequest, BroadcastResponse
from app.services.line_client import broadcast_text


router = APIRouter(dependencies=[Depends(require_admin)])


@router.post("/broadcast", response_model=BroadcastResponse, status_code=status.HTTP_202_ACCEPTED)
def broadcast(payload: BroadcastRequest) -> BroadcastResponse:
    broadcast_text(payload.message)
    return BroadcastResponse(status="queued")
