from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.student import Student


def create_student(db: Session, name: str, account_id: int) -> Student:
    student = Student(name=name, account_id=account_id)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def list_students_by_account(db: Session, account_id: int) -> list[Student]:
    return list(db.scalars(select(Student).where(Student.account_id == account_id).order_by(Student.name)))


def get_student(db: Session, student_id: int) -> Student | None:
    return db.get(Student, student_id)
