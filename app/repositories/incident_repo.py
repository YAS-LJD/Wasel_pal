from typing import List, Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident


async def get_all_incidents(
    db: AsyncSession,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    region: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> List[Incident]:
    offset = (page - 1) * limit
    filters = []
    params: dict = {"limit": limit, "offset": offset}

    if category:
        filters.append("category = :category")
        params["category"] = category
    if severity:
        filters.append("severity = :severity")
        params["severity"] = severity
    if status:
        filters.append("status = :status")
        params["status"] = status
    if region:
        filters.append("region ILIKE :region")
        params["region"] = f"%{region}%"
    if from_date:
        filters.append("created_at >= :from_date")
        params["from_date"] = from_date
    if to_date:
        filters.append("created_at <= :to_date")
        params["to_date"] = to_date

    where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""
    sql = text(
        f"SELECT * FROM incidents {where_clause} "
        f"ORDER BY created_at DESC "
        f"LIMIT :limit OFFSET :offset"
    )
    result = await db.execute(sql, params)
    rows = result.mappings().all()
    return [Incident(**dict(row)) for row in rows]


async def get_incident_by_id(db: AsyncSession, incident_id: int) -> Optional[Incident]:
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    return result.scalar_one_or_none()


async def create_incident(db: AsyncSession, data: dict) -> Incident:
    incident = Incident(**data)
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident


async def update_incident(
    db: AsyncSession, incident_id: int, data: dict
) -> Optional[Incident]:
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(incident, key, value)
    await db.commit()
    await db.refresh(incident)
    return incident


async def delete_incident(db: AsyncSession, incident_id: int) -> bool:
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        return False
    await db.delete(incident)
    await db.commit()
    return True


async def update_incident_status(
    db: AsyncSession, incident_id: int, new_status: str
) -> Optional[Incident]:
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        return None
    incident.status = new_status
    await db.commit()
    await db.refresh(incident)
    return incident