from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AccountCreate(BaseModel):
    line_user_id: str
    role: str = "member"


class AccountRead(BaseModel):
    id: int
    line_user_id: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
