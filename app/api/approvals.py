from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.database import get_db
from app.models import User
from app.schemas.approval import ApprovalCreate, ApprovalOut
from app.services import approval_service, audit_service

router = APIRouter(tags=["approvals"])


@router.post("/requests/{request_id}/approve", response_model=ApprovalOut)
def approve_request(
    request_id: int,
    payload: ApprovalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("ADMIN", "APPROVER")),
):
    approval = approval_service.approve_request(db, request_id, approver_id=user.id, payload=payload)
    audit_service.record(
        db, username=user.username, action="REQUEST_APPROVED",
        entity_type="request", entity_id=request_id,
    )
    db.commit()
    return approval


@router.post("/requests/{request_id}/reject", response_model=ApprovalOut)
def reject_request(
    request_id: int,
    payload: ApprovalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("ADMIN", "APPROVER")),
):
    approval = approval_service.reject_request(db, request_id, approver_id=user.id, payload=payload)
    audit_service.record(
        db, username=user.username, action="REQUEST_REJECTED",
        entity_type="request", entity_id=request_id,
    )
    db.commit()
    return approval
