from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


REQUEST_TYPES = ["FIREWALL", "SSL", "SFTP", "SERVER_ACCESS", "DNS"]
REQUEST_STATUSES = ["SUBMITTED", "APPROVED", "REJECTED", "COMPLETED"]


class RequestCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    request_type: str


class RequestUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    request_type: Optional[str] = None
    status: Optional[str] = None


class RequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    request_type: str
    status: str
    created_by: int
    created_date: datetime
    updated_date: datetime


class RequestList(BaseModel):
    total: int
    items: List[RequestOut]
