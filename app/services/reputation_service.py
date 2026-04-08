class ReputationService:
    def calculate_user_reputation(self, user_id: int) -> int:
        return 0
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models.user import User, UserRole
from app.schemas.user import UserUpdate, ReputationResponse
from app.core.security import hash_password

async def get_all_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()

async def get_user_by_id(user_id: int, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def update_user(user_id: int, data: UserUpdate, current_user: User, db: AsyncSession):
    user = await get_user_by_id(user_id, db)
    if current_user.role != UserRole.admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    if data.username:
        user.username = data.username
    if data.email:
        user.email = data.email
    if data.password:
        user.password_hash = hash_password(data.password)
    await db.commit()
    await db.refresh(user)
    return user

async def deactivate_user(user_id: int, db: AsyncSession):
    user = await get_user_by_id(user_id, db)
    user.is_active = False
    await db.commit()
    return {"message": "User deactivated"}

async def get_reputation(user_id: int, db: AsyncSession) -> ReputationResponse:
    user = await get_user_by_id(user_id, db)
    if user.total_reports >= 3:
        reputation = (user.valid_reports / user.total_reports) * 5.0
    else:
        reputation = user.reputation

    if reputation >= 4.0:
        level = "Trusted"
    elif reputation >= 2.5:
        level = "Regular"
    else:
        level = "New"

    return ReputationResponse(
        user_id=user.id,
        username=user.username,
        reputation=round(reputation, 2),
        total_reports=user.total_reports,
        valid_reports=user.valid_reports,
        level=level
    )