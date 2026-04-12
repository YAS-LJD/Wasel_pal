from datetime import datetime
from pydantic import BaseModel


class SubscriptionCreate(BaseModel):
    region:   str | None = None
    category: str | None = None


class SubscriptionResponse(BaseModel):
    id:        int
    region:    str | None
    category:  str | None
    is_active: bool

    model_config = {"from_attributes": True}


class AlertResponse(BaseModel):
    id:          int
    incident_id: int
    region:      str | None
    category:    str | None
    message:     str
    created_at:  datetime

    model_config = {"from_attributes": True}