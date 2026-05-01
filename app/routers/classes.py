from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app.schemas.training_class import TrainingClassCreate, TrainingClassRead
from app.services.class_service import create_class, list_classes


router = APIRouter()


@router.post("", response_model=TrainingClassRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_class_endpoint(payload: TrainingClassCreate, db: Session = Depends(get_db)):
    return create_class(db, name=payload.name, start_time=payload.start_time, end_time=payload.end_time)


@router.get("", response_model=list[TrainingClassRead])
def list_classes_endpoint(db: Session = Depends(get_db)):
    return list_classes(db)
