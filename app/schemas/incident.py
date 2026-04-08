from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.incident import IncidentCategory, IncidentSeverity, IncidentStatus


class IncidentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    region: Optional[str] = None
    category: IncidentCategory = IncidentCategory.other
    severity: IncidentSeverity = IncidentSeverity.medium
    latitude: float
    longitude: float
    checkpoint_id: Optional[int] = None


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    region: Optional[str] = None
    category: Optional[IncidentCategory] = None
    severity: Optional[IncidentSeverity] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    checkpoint_id: Optional[int] = None


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    region: Optional[str]
    category: IncidentCategory
    severity: IncidentSeverity
    status: IncidentStatus
    latitude: float
    longitude: float
    checkpoint_id: Optional[int]
    reported_by: Optional[int]
    cluster_size: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True