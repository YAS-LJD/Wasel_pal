from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    reputation: float
    is_active: bool

    class Config:
        from_attributes = True