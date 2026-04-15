import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.services.prediction_service import prediction_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predict", tags=["Predictions"])


@router.get("/checkpoint/{checkpoint_id}")
async def predict_checkpoint_status(
    checkpoint_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        result = await prediction_service.predict_checkpoint(checkpoint_id, db)
    except Exception as exc:
        logger.error(f"Prediction error for checkpoint {checkpoint_id}: {exc}")
        raise HTTPException(status_code=500, detail="Prediction service encountered an error.")
    return result


@router.get("/region/{region}")
async def predict_region_activity(
    region: str = Path(..., min_length=2),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        result = await prediction_service.predict_region(region, db)
    except Exception as exc:
        logger.error(f"Region prediction error for '{region}': {exc}")
        raise HTTPException(status_code=500, detail="Prediction service encountered an error.")
    return result