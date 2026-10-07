from typing import List

from pydantic import BaseModel


class RequestsByType(BaseModel):
    request_type: str
    count: int


class DashboardResponse(BaseModel):
    total_requests: int
    submitted_requests: int
    approved_requests: int
    rejected_requests: int
    completed_requests: int
    requests_by_type: List[RequestsByType]
