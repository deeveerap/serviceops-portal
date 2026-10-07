from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    request_type = Column(String(32), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="SUBMITTED", index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_date = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    created_by_user = relationship("User", back_populates="requests")
    approvals = relationship("Approval", back_populates="request")
    notifications = relationship("Notification", back_populates="request")
