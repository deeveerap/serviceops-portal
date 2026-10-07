from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models import Notification, Request
from app.schemas.request import REQUEST_STATUSES, REQUEST_TYPES, RequestCreate, RequestUpdate


def validate_type(request_type: str) -> None:
    if request_type not in REQUEST_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid request_type: {request_type}")


def validate_status(status: str) -> None:
    if status not in REQUEST_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")


def create_request(
    db: Session, payload: RequestCreate, created_by: int
) -> Request:
    validate_type(payload.request_type)
    req = Request(
        title=payload.title,
        description=payload.description,
        request_type=payload.request_type,
        created_by=created_by,
        status="SUBMITTED",
    )
    db.add(req)
    db.flush()

    db.add(
        Notification(
            request_id=req.id,
            recipient="approvers@example.com",
            message=f"New request submitted: {req.title}",
            status="PENDING",
        )
    )
    db.commit()
    db.refresh(req)
    return req


def list_requests(
    db: Session, status: Optional[str] = None, request_type: Optional[str] = None
) -> List[Request]:
    query = db.query(Request)
    if status:
        validate_status(status)
        query = query.filter(Request.status == status)
    if request_type:
        validate_type(request_type)
        query = query.filter(Request.request_type == request_type)
    return query.order_by(desc(Request.created_date)).all()


def get_request(db: Session, request_id: int) -> Request:
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req


def update_request(
    db: Session, request_id: int, payload: RequestUpdate
) -> Request:
    req = get_request(db, request_id)
    if payload.title is not None:
        req.title = payload.title
    if payload.description is not None:
        req.description = payload.description
    if payload.request_type is not None:
        validate_type(payload.request_type)
        req.request_type = payload.request_type
    if payload.status is not None:
        validate_status(payload.status)
        req.status = payload.status
    db.commit()
    db.refresh(req)
    return req


def delete_request(db: Session, request_id: int) -> None:
    req = get_request(db, request_id)
    db.delete(req)
    db.commit()
