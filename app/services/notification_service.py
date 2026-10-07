import logging
from typing import List

from sqlalchemy.orm import Session

from app.models import Notification

logger = logging.getLogger(__name__)


def get_pending(db: Session, limit: int = 50) -> List[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.status == "PENDING")
        .order_by(Notification.created_date.asc())
        .limit(limit)
        .all()
    )


def mark_sent(db: Session, notification: Notification) -> None:
    notification.status = "SENT"
    db.commit()
    logger.info(
        "notification_sent id=%s request_id=%s recipient=%s",
        notification.id,
        notification.request_id,
        notification.recipient,
    )
