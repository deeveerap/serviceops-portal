from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False, index=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approval_status = Column(String(32), nullable=False)
    comments = Column(Text, nullable=True)
    approved_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    request = relationship("Request", back_populates="approvals")
    approver = relationship("User", back_populates="approvals")
