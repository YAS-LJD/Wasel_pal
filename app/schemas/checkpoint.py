from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.checkpoint import CheckpointStatus, CheckpointType

class CheckpointCreate(BaseModel):
    name:        str
    name_ar:     Optional[str] = None
    region:      Optional[str] = None
    type:        CheckpointType = CheckpointType.military
    latitude:    float
    longitude:   float
    description: Optional[str] = None

class CheckpointUpdate(BaseModel):
    name:        Optional[str]            = None
    name_ar:     Optional[str]            = None
    region:      Optional[str]            = None
    type:        Optional[CheckpointType] = None
    latitude:    Optional[float]          = None
    longitude:   Optional[float]          = None
    description: Optional[str]            = None

class CheckpointStatusUpdate(BaseModel):
    status: CheckpointStatus
    reason: Optional[str] = None

class CheckpointStatusHistoryResponse(BaseModel):
    id:         int
    old_status: Optional[str]
    new_status: str
    changed_by: Optional[int]
    reason:     Optional[str]
    changed_at: datetime

    class Config:
        from_attributes = True

class CheckpointResponse(BaseModel):
    id:          int
    name:        str
    name_ar:     Optional[str]
    region:      Optional[str]
    type:        CheckpointType
    status:      CheckpointStatus
    latitude:    float
    longitude:   float
    description: Optional[str]
    created_at:  datetime
    updated_at:  datetime

    class Config:
        from_attributes = True