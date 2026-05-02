from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account


def get_account_by_line_user_id(db: Session, line_user_id: str) -> Account | None:
    return db.scalar(select(Account).where(Account.line_user_id == line_user_id))


def get_or_create_account(db: Session, line_user_id: str, role: str = "member") -> Account:
    account = get_account_by_line_user_id(db, line_user_id)
    if account:
        return account

    account = Account(line_user_id=line_user_id, role=role)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account
