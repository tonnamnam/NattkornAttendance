from datetime import datetime, time

from sqlalchemy import DateTime, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TrainingClass(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    attendances: Mapped[list["Attendance"]] = relationship(back_populates="training_class", cascade="all, delete-orphan")
