from pydantic import BaseModel


class CheckpointCreate(BaseModel):
    name: str
    latitude: float
    longitude: float


class CheckpointResponse(CheckpointCreate):
    id: int
    status: str

    class Config:
        from_attributes = True
