from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checkpoint import Checkpoint, CheckpointStatusHistory
from sqlalchemy import select


async def get_all_checkpoints(
    db: AsyncSession,
    region: Optional[str] = None,
    status: Optional[str] = None,
    type: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",
    order: str = "desc",
) -> List[Checkpoint]:
    allowed_sort = {"id", "name", "created_at", "status", "region"}
    if sort_by not in allowed_sort:
        sort_by = "created_at"
    order_clause = "DESC" if order.lower() == "desc" else "ASC"
    offset = (page - 1) * limit

    filters = []
    params: dict = {"limit": limit, "offset": offset}

    if region:
        filters.append("region ILIKE :region")
        params["region"] = f"%{region}%"
    if status:
        filters.append("status = :status")
        params["status"] = status
    if type:
        filters.append("type = :type")
        params["type"] = type

    where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""
    sql = text(
        f"SELECT * FROM checkpoints {where_clause} "
        f"ORDER BY {sort_by} {order_clause} "
        f"LIMIT :limit OFFSET :offset"
    )
    result = await db.execute(sql, params)
    rows = result.mappings().all()
    return [Checkpoint(**dict(row)) for row in rows]


async def get_checkpoint_by_id(db: AsyncSession, checkpoint_id: int) -> Optional[Checkpoint]:
    result = await db.execute(select(Checkpoint).where(Checkpoint.id == checkpoint_id))
    return result.scalar_one_or_none()


async def create_checkpoint(db: AsyncSession, data: dict) -> Checkpoint:
    clean = {k: (v.value if hasattr(v, "value") else v) for k, v in data.items()}
    checkpoint = Checkpoint(**clean)
    db.add(checkpoint)
    await db.commit()
    await db.refresh(checkpoint)
    return checkpoint


async def update_checkpoint(
    db: AsyncSession, checkpoint_id: int, data: dict
) -> Optional[Checkpoint]:
    result = await db.execute(select(Checkpoint).where(Checkpoint.id == checkpoint_id))
    checkpoint = result.scalar_one_or_none()
    if not checkpoint:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(checkpoint, key, value)
    await db.commit()
    await db.refresh(checkpoint)
    return checkpoint


async def delete_checkpoint(db: AsyncSession, checkpoint_id: int) -> bool:
    result = await db.execute(select(Checkpoint).where(Checkpoint.id == checkpoint_id))
    checkpoint = result.scalar_one_or_none()
    if not checkpoint:
        return False
    await db.delete(checkpoint)
    await db.commit()
    return True


async def update_checkpoint_status(
    db: AsyncSession,
    checkpoint_id: int,
    new_status: str,
    changed_by: Optional[int],
    reason: Optional[str],
) -> Optional[Checkpoint]:
    result = await db.execute(select(Checkpoint).where(Checkpoint.id == checkpoint_id))
    checkpoint = result.scalar_one_or_none()
    if not checkpoint:
        return None

    history = CheckpointStatusHistory(
        checkpoint_id=checkpoint_id,
        old_status=checkpoint.status,
        new_status=new_status,
        changed_by=changed_by,
        reason=reason,
    )
    db.add(history)
    checkpoint.status = new_status
    await db.commit()
    await db.refresh(checkpoint)
    return checkpoint


async def get_checkpoint_history(
    db: AsyncSession, checkpoint_id: int
) -> List[CheckpointStatusHistory]:
    result = await db.execute(
        select(CheckpointStatusHistory)
        .where(CheckpointStatusHistory.checkpoint_id == checkpoint_id)
        .order_by(CheckpointStatusHistory.changed_at.desc())
    )
    return result.scalars().all()