from pydantic import BaseModel


class IncidentCreate(BaseModel):
    title: str
    description: str | None = None
    latitude: float
    longitude: float
    severity: str = "medium"


class IncidentResponse(IncidentCreate):
    id: int

    class Config:
        from_attributes = True
