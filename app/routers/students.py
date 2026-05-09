from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app.models.account import Account
from app.schemas.student import (
    AccountStudentLinkCreate,
    AccountStudentLinkRead,
    StudentCreate,
    StudentRead,
    StudentWithAccountCreate,
)
from app.services.student_service import (
    DuplicateAccountStudentLinkError,
    DuplicateStudentAccessCodeError,
    create_student,
    get_student,
    link_account_to_student,
)


router = APIRouter()


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_student_endpoint(payload: StudentCreate, db: Session = Depends(get_db)):
    try:
        return create_student(db, name=payload.name, access_code=payload.access_code)
    except DuplicateStudentAccessCodeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/with-account",
    response_model=StudentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_student_with_account_endpoint(payload: StudentWithAccountCreate, db: Session = Depends(get_db)):
    account = db.get(Account, payload.account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")

    try:
        student = create_student(db, name=payload.name, access_code=payload.access_code)
    except DuplicateStudentAccessCodeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    link_account_to_student(db, account_id=payload.account_id, student_id=student.id, relationship=payload.relationship)
    return student


@router.post(
    "/link",
    response_model=AccountStudentLinkRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def link_account_to_student_endpoint(payload: AccountStudentLinkCreate, db: Session = Depends(get_db)):
    account = db.get(Account, payload.account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")

    student = get_student(db, payload.student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    try:
        return link_account_to_student(
            db,
            account_id=payload.account_id,
            student_id=payload.student_id,
            relationship=payload.relationship,
        )
    except DuplicateAccountStudentLinkError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/{student_id}", response_model=StudentRead)
def get_student_endpoint(student_id: int, db: Session = Depends(get_db)):
    student = get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return student
