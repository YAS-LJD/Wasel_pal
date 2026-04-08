from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import checkpoint_repo
from app.schemas.checkpoint import (
    CheckpointCreate,
    CheckpointStatusUpdate,
    CheckpointUpdate,
)


async def list_checkpoints(
    db: AsyncSession,
    region: Optional[str] = None,
    status: Optional[str] = None,
    type: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",
    order: str = "desc",
):
    return await checkpoint_repo.get_all_checkpoints(
        db, region=region, status=status, type=type,
        page=page, limit=limit, sort_by=sort_by, order=order
    )


async def get_checkpoint(db: AsyncSession, checkpoint_id: int):
    checkpoint = await checkpoint_repo.get_checkpoint_by_id(db, checkpoint_id)
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return checkpoint


async def create_checkpoint(db: AsyncSession, data: CheckpointCreate):
    return await checkpoint_repo.create_checkpoint(db, data.model_dump(mode="python"))


async def update_checkpoint(db: AsyncSession, checkpoint_id: int, data: CheckpointUpdate):
    checkpoint = await checkpoint_repo.update_checkpoint(
        db, checkpoint_id, data.model_dump(mode="python", exclude_none=True)
    )
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return checkpoint


async def delete_checkpoint(db: AsyncSession, checkpoint_id: int):
    deleted = await checkpoint_repo.delete_checkpoint(db, checkpoint_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return {"detail": "Checkpoint deleted"}


async def change_checkpoint_status(
    db: AsyncSession,
    checkpoint_id: int,
    data: CheckpointStatusUpdate,
    user_id: int,
):
    checkpoint = await checkpoint_repo.update_checkpoint_status(
        db, checkpoint_id, data.status.value, user_id, data.reason
    )
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return checkpoint


async def get_checkpoint_history(db: AsyncSession, checkpoint_id: int):
    await get_checkpoint(db, checkpoint_id)
    return await checkpoint_repo.get_checkpoint_history(db, checkpoint_id)