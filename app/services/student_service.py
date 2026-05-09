import secrets
import string

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.account_student import AccountStudent
from app.models.student import Student


class DuplicateAccountStudentLinkError(Exception):
    pass


class DuplicateStudentAccessCodeError(Exception):
    pass


def normalize_access_code(access_code: str) -> str:
    return "".join(access_code.split()).upper()


def generate_access_code(db: Session) -> str:
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(20):
        access_code = "".join(secrets.choice(alphabet) for _ in range(6))
        if not get_student_by_access_code(db, access_code):
            return access_code
    raise RuntimeError("Could not generate a unique student access code.")


def create_student(db: Session, name: str, access_code: str | None = None) -> Student:
    normalized_code = normalize_access_code(access_code) if access_code else ""
    student = Student(name=name, access_code=normalized_code or generate_access_code(db))
    db.add(student)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateStudentAccessCodeError("Student access code is already in use.") from exc
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


def get_student_by_access_code(db: Session, access_code: str) -> Student | None:
    normalized_code = normalize_access_code(access_code)
    if not normalized_code:
        return None
    return db.scalar(select(Student).where(Student.access_code == normalized_code))


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
