from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.security import create_access_token, verify_password
from app.auth.blocklist import revoke
from app.database import get_db
from app.models import User
from app.schemas.user import LoginResponse, LogoutResponse, UserOut
from app.services.audit_service import record as audit_record
from app.utils.metrics import login_total

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        login_total.labels(outcome="failure").inc()
        audit_record(
            db,
            username=form_data.username,
            action="LOGIN_FAILED",
            entity_type="user",
        )
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=user.username, role=user.role)
    login_total.labels(outcome="success").inc()
    audit_record(
        db,
        username=user.username,
        action="LOGIN",
        entity_type="user",
        entity_id=user.id,
    )
    db.commit()
    return LoginResponse(access_token=token)


@router.post("/logout", response_model=LogoutResponse)
def logout(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    auth_header = request.headers.get("authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()
    if token:
        revoke(token)
    audit_record(
        db, username=user.username, action="LOGOUT", entity_type="user", entity_id=user.id
    )
    db.commit()
    return LogoutResponse(message="Logged out successfully")


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
