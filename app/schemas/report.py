from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.report import ReportCategory, ReportStatus


class ReportCreate(BaseModel):
    latitude: float
    longitude: float
    category: ReportCategory
    description: Optional[str] = None


class ReportModerate(BaseModel):
    status: ReportStatus
    confidence: Optional[float] = None


class VoteCreate(BaseModel):
    vote: str              # up, down


class ReportResponse(BaseModel):
    id: int
    user_id: int
    latitude: float
    longitude: float
    category: str
    description: Optional[str]
    status: str
    confidence: float
    upvotes: int
    downvotes: int
    created_at: datetime

    class Config:
        from_attributes = True