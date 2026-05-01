from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app.models.account import Account
from app.schemas.student import StudentCreate, StudentRead
from app.services.student_service import create_student, get_student


router = APIRouter()


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_student_endpoint(payload: StudentCreate, db: Session = Depends(get_db)):
    account = db.get(Account, payload.account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")
    return create_student(db, name=payload.name, account_id=payload.account_id)


@router.get("/{student_id}", response_model=StudentRead)
def get_student_endpoint(student_id: int, db: Session = Depends(get_db)):
    student = get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return student
