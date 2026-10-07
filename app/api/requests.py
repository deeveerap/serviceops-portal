from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.database import get_db
from app.models import User
from app.schemas.request import RequestCreate, RequestList, RequestOut, RequestUpdate
from app.services import audit_service, request_service
from app.utils.metrics import request_creation_total

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=RequestOut, status_code=status.HTTP_201_CREATED)
def create_request(
    payload: RequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    req = request_service.create_request(db, payload, created_by=user.id)
    request_creation_total.labels(request_type=req.request_type).inc()
    audit_service.record(
        db, username=user.username, action="REQUEST_CREATED",
        entity_type="request", entity_id=req.id,
    )
    db.commit()
    return req


@router.get("", response_model=RequestList)
def list_requests(
    status: Optional[str] = Query(None),
    request_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items = request_service.list_requests(db, status=status, request_type=request_type)
    return RequestList(total=len(items), items=items)


@router.get("/{request_id}", response_model=RequestOut)
def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return request_service.get_request(db, request_id)


@router.put("/{request_id}", response_model=RequestOut)
def update_request(
    request_id: int,
    payload: RequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    req = request_service.update_request(db, request_id, payload)
    audit_service.record(
        db, username=user.username, action="REQUEST_UPDATED",
        entity_type="request", entity_id=req.id,
    )
    db.commit()
    return req


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("ADMIN", "OPERATOR")),
):
    request_service.delete_request(db, request_id)
    audit_service.record(
        db, username=user.username, action="REQUEST_DELETED",
        entity_type="request", entity_id=request_id,
    )
    db.commit()
    return None
