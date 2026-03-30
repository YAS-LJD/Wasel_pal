from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserResponse
from app.services.auth_service import register, login
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
async def register_user(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await register(data, db)

@router.post("/login", response_model=TokenResponse)
async def login_user(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await login(data, db)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user