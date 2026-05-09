from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StudentCreate(BaseModel):
    name: str
    access_code: str | None = None


class StudentWithAccountCreate(BaseModel):
    name: str
    access_code: str | None = None
    account_id: int
    relationship: str = "self"


class AccountStudentLinkCreate(BaseModel):
    account_id: int
    student_id: int
    relationship: str = "self"


class AccountStudentLinkRead(BaseModel):
    id: int
    account_id: int
    student_id: int
    relationship: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentRead(BaseModel):
    id: int
    name: str
    access_code: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
