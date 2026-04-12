from pydantic import BaseModel


class RouteRequest(BaseModel):
    source_lat: float
    source_lng: float
    dest_lat: float
    dest_lng: float
    strategy: str = "balanced"


class RouteResponse(BaseModel):
    strategy:   str
    path:       list[dict]
    eta_minutes: int
    risk_score: float
    meta:       str | None = None

    model_config = {"extra": "allow"}  # يسمح بالحقول الإضافية لكل strategy