from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship as sa_relationship

from app.db.session import Base


class AccountStudent(Base):
    __tablename__ = "account_students"
    __table_args__ = (
        UniqueConstraint("account_id", "student_id", name="uq_account_student"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    relationship: Mapped[str] = mapped_column(String(40), default="self", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    account: Mapped["Account"] = sa_relationship(back_populates="student_links")
    student: Mapped["Student"] = sa_relationship(back_populates="account_links")
