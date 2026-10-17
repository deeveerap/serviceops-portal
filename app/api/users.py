from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate, UserOut
from app.services import user_service
from app.services.audit_service import record as audit_record

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
):
    return db.query(User).order_by(User.id).all()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    user = user_service.create_user(db, payload)
    audit_record(
        db,
        username=current_user.username,
        action="USER_CREATED",
        entity_type="user",
        entity_id=user.id,
    )
    db.commit()
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete the currently authenticated user")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    audit_record(
        db,
        username=current_user.username,
        action="USER_DELETED",
        entity_type="user",
        entity_id=user_id,
    )
    db.commit()
    return None
