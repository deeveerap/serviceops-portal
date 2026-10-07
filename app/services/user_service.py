from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserCreate
from app.auth.security import hash_password


def create_user(db: Session, payload: UserCreate) -> User:
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
