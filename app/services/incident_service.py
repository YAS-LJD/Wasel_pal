from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import incident_repo
from app.schemas.incident import IncidentCreate, IncidentStatusUpdate, IncidentUpdate


async def list_incidents(
    db: AsyncSession,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    region: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
):
    return await incident_repo.get_all_incidents(
        db,
        category=category,
        severity=severity,
        status=status,
        region=region,
        from_date=from_date,
        to_date=to_date,
        page=page,
        limit=limit,
    )


async def get_incident(db: AsyncSession, incident_id: int):
    incident = await incident_repo.get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


async def create_incident(db: AsyncSession, data: IncidentCreate, user_id: int):
    payload = data.model_dump()
    payload["reported_by"] = user_id
    return await incident_repo.create_incident(db, payload)


async def update_incident(db: AsyncSession, incident_id: int, data: IncidentUpdate):
    incident = await incident_repo.update_incident(
        db, incident_id, data.model_dump(exclude_none=True)
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


async def delete_incident(db: AsyncSession, incident_id: int):
    deleted = await incident_repo.delete_incident(db, incident_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"detail": "Incident deleted"}


async def change_incident_status(
    db: AsyncSession, incident_id: int, data: IncidentStatusUpdate
):
    incident = await incident_repo.update_incident_status(
        db, incident_id, data.status.value
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident