from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_admin, require_moderator
from app.database import get_db
from app.models.user import User
from app.schemas.checkpoint import (
    CheckpointCreate,
    CheckpointResponse,
    CheckpointStatusHistoryResponse,
    CheckpointStatusUpdate,
    CheckpointUpdate,
)
from app.services import checkpoint_service

router = APIRouter(prefix="/checkpoints", tags=["Checkpoints"])


@router.get("", response_model=List[CheckpointResponse])
async def list_checkpoints(
    region: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
):
    return await checkpoint_service.list_checkpoints(
        db, region=region, status=status, type=type,
        page=page, limit=limit, sort_by=sort_by, order=order
    )


@router.get("/{checkpoint_id}", response_model=CheckpointResponse)
async def get_checkpoint(
    checkpoint_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await checkpoint_service.get_checkpoint(db, checkpoint_id)


@router.post("", response_model=CheckpointResponse, status_code=201)
async def create_checkpoint(
    data: CheckpointCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator),
):
    return await checkpoint_service.create_checkpoint(db, data)


@router.put("/{checkpoint_id}", response_model=CheckpointResponse)
async def update_checkpoint(
    checkpoint_id: int,
    data: CheckpointUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator),
):
    return await checkpoint_service.update_checkpoint(db, checkpoint_id, data)


@router.delete("/{checkpoint_id}")
async def delete_checkpoint(
    checkpoint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await checkpoint_service.delete_checkpoint(db, checkpoint_id)


@router.patch("/{checkpoint_id}/status", response_model=CheckpointResponse)
async def update_checkpoint_status(
    checkpoint_id: int,
    data: CheckpointStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator),
):
    return await checkpoint_service.change_checkpoint_status(
        db, checkpoint_id, data, current_user.id
    )


@router.get("/{checkpoint_id}/history", response_model=List[CheckpointStatusHistoryResponse])
async def get_checkpoint_history(
    checkpoint_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await checkpoint_service.get_checkpoint_history(db, checkpoint_id)