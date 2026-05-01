from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.attendance import Attendance


class DuplicateAttendanceError(Exception):
    pass


def create_attendance(db: Session, student_id: int, class_id: int, check_in_time: datetime | None = None) -> Attendance:
    checked_at = check_in_time or datetime.now()
    attendance = Attendance(
        student_id=student_id,
        class_id=class_id,
        attendance_date=checked_at.date(),
        check_in_time=checked_at,
    )
    db.add(attendance)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateAttendanceError("Student already checked in for this class today.") from exc

    db.refresh(attendance)
    return attendance


def list_attendance_report(db: Session, start_date: date, end_date: date) -> list[Attendance]:
    statement = (
        select(Attendance)
        .where(Attendance.attendance_date >= start_date)
        .where(Attendance.attendance_date <= end_date)
        .order_by(Attendance.attendance_date, Attendance.check_in_time)
    )
    return list(db.scalars(statement))
