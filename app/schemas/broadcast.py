from pydantic import BaseModel, Field


class BroadcastRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)


class BroadcastResponse(BaseModel):
    status: str
