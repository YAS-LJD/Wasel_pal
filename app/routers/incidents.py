from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_admin, require_moderator
from app.database import get_db
from app.models.user import User
from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentStatusUpdate,
    IncidentUpdate,
)
from app.services.incident_service import (
    list_incidents   as svc_list,
    get_incident     as svc_get,
    create_incident  as svc_create,
    update_incident  as svc_update,
    delete_incident  as svc_delete,
    change_incident_status as svc_status,
)

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=List[IncidentResponse])
async def list_incidents(
    category:  Optional[str] = Query(None),
    severity:  Optional[str] = Query(None),
    status:    Optional[str] = Query(None),
    region:    Optional[str] = Query(None),
    from_date: Optional[str] = Query(None, alias="from"),
    to_date:   Optional[str] = Query(None, alias="to"),
    page:  int = Query(1,  ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await svc_list(
        db, category=category, severity=severity, status=status,
        region=region, from_date=from_date, to_date=to_date,
        page=page, limit=limit,
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: int, db: AsyncSession = Depends(get_db)):
    return await svc_get(db, incident_id)


@router.post("", response_model=IncidentResponse, status_code=201)
async def create_incident(
    data: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator),
):
    return await svc_create(db, data, current_user.id)


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    data: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator),
):
    return await svc_update(db, incident_id, data)


@router.delete("/{incident_id}")
async def delete_incident(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await svc_delete(db, incident_id)


@router.patch("/{incident_id}/status", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: int,
    data: IncidentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator),
):
    return await svc_status(db, incident_id, data)