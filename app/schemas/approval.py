from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ApprovalCreate(BaseModel):
    comments: Optional[str] = Field(None, max_length=2000)


class ApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int
    approved_by: int
    approval_status: str
    comments: Optional[str]
    approved_date: datetime
