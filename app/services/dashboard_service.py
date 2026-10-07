from collections import Counter

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Request
from app.schemas.dashboard import DashboardResponse, RequestsByType


def get_dashboard(db: Session) -> DashboardResponse:
    status_counts = dict(
        db.query(Request.status, func.count(Request.id))
        .group_by(Request.status)
        .all()
    )

    type_counts = dict(
        db.query(Request.request_type, func.count(Request.id))
        .group_by(Request.request_type)
        .all()
    )

    requests_by_type = [
        RequestsByType(request_type=t, count=c) for t, c in sorted(type_counts.items())
    ]

    return DashboardResponse(
        total_requests=sum(status_counts.values()),
        submitted_requests=status_counts.get("SUBMITTED", 0),
        approved_requests=status_counts.get("APPROVED", 0),
        rejected_requests=status_counts.get("REJECTED", 0),
        completed_requests=status_counts.get("COMPLETED", 0),
        requests_by_type=requests_by_type,
    )
