from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Approval, Notification, Request
from app.schemas.approval import ApprovalCreate


def _set_request_status(db: Session, req: Request, status: str) -> None:
    req.status = status
    db.add(
        Notification(
            request_id=req.id,
            recipient=f"user{req.created_by}@example.com",
            message=f"Request {req.id} is now {status}",
            status="PENDING",
        )
    )


def approve_request(
    db: Session, request_id: int, approver_id: int, payload: ApprovalCreate
) -> Approval:
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status not in ("SUBMITTED",):
        raise HTTPException(
            status_code=400, detail=f"Cannot approve request in status {req.status}"
        )

    approval = Approval(
        request_id=request_id,
        approved_by=approver_id,
        approval_status="APPROVED",
        comments=payload.comments,
    )
    db.add(approval)
    _set_request_status(db, req, "APPROVED")
    db.commit()
    db.refresh(approval)
    return approval


def reject_request(
    db: Session, request_id: int, approver_id: int, payload: ApprovalCreate
) -> Approval:
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status not in ("SUBMITTED",):
        raise HTTPException(
            status_code=400, detail=f"Cannot reject request in status {req.status}"
        )

    approval = Approval(
        request_id=request_id,
        approved_by=approver_id,
        approval_status="REJECTED",
        comments=payload.comments,
    )
    db.add(approval)
    _set_request_status(db, req, "REJECTED")
    db.commit()
    db.refresh(approval)
    return approval
