from pydantic import BaseModel


class ReportCreate(BaseModel):
    type: str
    content: str


class ReportResponse(ReportCreate):
    id: int
    status: str

    class Config:
        from_attributes = True
