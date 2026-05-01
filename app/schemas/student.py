from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StudentCreate(BaseModel):
    name: str
    account_id: int


class StudentRead(BaseModel):
    id: int
    name: str
    account_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
