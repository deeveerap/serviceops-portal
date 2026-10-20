from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserCreate
from app.auth.security import hash_password


@dataclass
class UserCreateInternal:
    username: str
    password: str
    role: str = "USER"


def _create_user(db: Session, *, username: str, password: str, role: str) -> User:
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=username,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_user(db: Session, payload: UserCreate) -> User:
    return _create_user(
        db,
        username=payload.username,
        password=payload.password,
        role=payload.role,
    )


def create_user_internal(db: Session, payload: UserCreateInternal) -> User:
    return _create_user(
        db,
        username=payload.username,
        password=payload.password,
        role=payload.role,
    )
