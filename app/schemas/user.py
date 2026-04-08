from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    reputation: float
    total_reports: int
    valid_reports: int
    is_active: bool

    class Config:
        from_attributes = True

class ReputationResponse(BaseModel):
    user_id: int
    username: str
    reputation: float
    total_reports: int
    valid_reports: int
    level: str