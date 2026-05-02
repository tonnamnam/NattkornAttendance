from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountRead
from app.services.account_service import get_or_create_account


router = APIRouter(dependencies=[Depends(require_admin)])


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def create_account_endpoint(payload: AccountCreate, db: Session = Depends(get_db)):
    return get_or_create_account(db, payload.line_user_id, role=payload.role)


@router.get("", response_model=list[AccountRead])
def list_accounts_endpoint(db: Session = Depends(get_db)):
    return list(db.scalars(select(Account).order_by(Account.created_at.desc())))
