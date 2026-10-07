from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, default="USER")
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    requests = relationship("Request", back_populates="created_by_user")
    approvals = relationship("Approval", back_populates="approver")
