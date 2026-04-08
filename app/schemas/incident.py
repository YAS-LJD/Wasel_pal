from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from app.models.incident import IncidentCategory, IncidentSeverity, IncidentStatus

def strip_tz(v):
    if v is None:
        return v
    if isinstance(v, str):
        v = datetime.fromisoformat(v.replace("Z", "+00:00"))
    if hasattr(v, "tzinfo") and v.tzinfo is not None:
        return v.replace(tzinfo=None)
    return v

class IncidentCreate(BaseModel):
    title:         str
    description:   Optional[str]      = None
    region:        Optional[str]      = None
    category:      IncidentCategory
    severity:      IncidentSeverity   = IncidentSeverity.medium
    latitude:      Optional[float]    = None
    longitude:     Optional[float]    = None
    checkpoint_id: Optional[int]      = None
    starts_at:     Optional[datetime] = None
    ends_at:       Optional[datetime] = None

    @field_validator("starts_at", "ends_at", mode="before")
    @classmethod
    def remove_tz(cls, v): return strip_tz(v)

class IncidentUpdate(BaseModel):
    title:         Optional[str]              = None
    description:   Optional[str]              = None
    region:        Optional[str]              = None
    category:      Optional[IncidentCategory] = None
    severity:      Optional[IncidentSeverity] = None
    latitude:      Optional[float]            = None
    longitude:     Optional[float]            = None
    checkpoint_id: Optional[int]              = None
    starts_at:     Optional[datetime]         = None
    ends_at:       Optional[datetime]         = None

    @field_validator("starts_at", "ends_at", mode="before")
    @classmethod
    def remove_tz(cls, v): return strip_tz(v)

class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus

class IncidentResponse(BaseModel):
    id:            int
    title:         str
    description:   Optional[str]
    region:        Optional[str]
    category:      IncidentCategory
    severity:      IncidentSeverity
    status:        IncidentStatus
    latitude:      Optional[float]
    longitude:     Optional[float]
    checkpoint_id: Optional[int]
    reported_by:   Optional[int]
    verified_by:   Optional[int]
    cluster_id:    Optional[int]
    starts_at:     Optional[datetime]
    ends_at:       Optional[datetime]
    created_at:    datetime
    updated_at:    datetime

    class Config:
        from_attributes = True