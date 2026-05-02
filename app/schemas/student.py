from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StudentCreate(BaseModel):
    name: str


class StudentWithAccountCreate(BaseModel):
    name: str
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
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
