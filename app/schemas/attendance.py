from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class AttendanceRead(BaseModel):
    id: int
    student_id: int
    class_id: int
    attendance_date: date
    check_in_time: datetime

    model_config = ConfigDict(from_attributes=True)
