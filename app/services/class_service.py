from datetime import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.training_class import TrainingClass


def create_class(db: Session, name: str, start_time: time, end_time: time) -> TrainingClass:
    training_class = TrainingClass(name=name, start_time=start_time, end_time=end_time)
    db.add(training_class)
    db.commit()
    db.refresh(training_class)
    return training_class


def list_classes(db: Session) -> list[TrainingClass]:
    return list(db.scalars(select(TrainingClass).order_by(TrainingClass.start_time, TrainingClass.name)))


def get_class(db: Session, class_id: int) -> TrainingClass | None:
    return db.get(TrainingClass, class_id)
