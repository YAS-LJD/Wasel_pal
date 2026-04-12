from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.schemas.route import RouteRequest, RouteResponse
from app.services.route_service import RouteService

router = APIRouter(prefix="/routes", tags=["Routes"])
_svc   = RouteService()


@router.post("/estimate", response_model=RouteResponse)
async def estimate_route(
    body: RouteRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    result = await _svc.build_route(db, body.model_dump())
    return result


@router.get("/strategies")
async def list_strategies():
    return [
        {"name": "fastest",  "description": "أسرع مسار — يمر على كل الحواجز"},
        {"name": "safest",   "description": "أأمن مسار — يتجنب المغلق والمقيد"},
        {"name": "balanced", "description": "توازن بين الوقت والسلامة"},
    ]