from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False, index=True)
    recipient = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="PENDING", index=True)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    request = relationship("Request", back_populates="notifications")
