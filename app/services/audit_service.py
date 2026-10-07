from typing import Optional

from sqlalchemy.orm import Session

from app.models import AuditLog


def record(
    db: Session,
    username: str,
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
) -> AuditLog:
    entry = AuditLog(
        username=username,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    db.add(entry)
    db.flush()
    return entry
