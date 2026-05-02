from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.account_student import AccountStudent
from app.models.student import Student


class DuplicateAccountStudentLinkError(Exception):
    pass


def create_student(db: Session, name: str) -> Student:
    student = Student(name=name)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def list_students_by_account(db: Session, account_id: int) -> list[Student]:
    statement = (
        select(Student)
        .join(AccountStudent, AccountStudent.student_id == Student.id)
        .where(AccountStudent.account_id == account_id)
        .order_by(Student.name)
    )
    return list(db.scalars(statement))


def get_student(db: Session, student_id: int) -> Student | None:
    return db.get(Student, student_id)


def link_account_to_student(db: Session, account_id: int, student_id: int, relationship: str = "self") -> AccountStudent:
    link = AccountStudent(account_id=account_id, student_id=student_id, relationship=relationship)
    db.add(link)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateAccountStudentLinkError("Account is already linked to this student.") from exc
    db.refresh(link)
    return link


def account_can_access_student(db: Session, account_id: int, student_id: int) -> bool:
    statement = (
        select(AccountStudent.id)
        .where(AccountStudent.account_id == account_id)
        .where(AccountStudent.student_id == student_id)
    )
    return db.scalar(statement) is not None
