import logging
from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.cache_service import TTL_PREDICTION, cache_service

logger = logging.getLogger(__name__)

WEIGHT_RECENT_CLOSURE  = 0.40
WEIGHT_INCIDENT_ACTIVE = 0.30
WEIGHT_HOUR_OF_DAY     = 0.15
WEIGHT_DAY_OF_WEEK     = 0.10
WEIGHT_REPORT_VOLUME   = 0.05

def _hour_risk(hour):
    if 0 <= hour < 5:   return 0.7
    if 5 <= hour < 8:   return 0.4
    if 8 <= hour < 17:  return 0.2
    if 17 <= hour < 20: return 0.3
    return 0.5

def _dow_risk(weekday):
    return {0:0.2,1:0.2,2:0.2,3:0.25,4:0.5,5:0.45,6:0.25}.get(weekday,0.25)

def _score_to_label(score):
    if score >= 0.75: return "critical"
    if score >= 0.55: return "high"
    if score >= 0.35: return "medium"
    return "low"

def _score_to_status(score):
    if score >= 0.75: return "closed"
    if score >= 0.55: return "restricted"
    if score >= 0.35: return "delayed"
    return "open"

class PredictionService:

    async def predict_checkpoint(self, checkpoint_id, db):
        cache_key = cache_service.prediction_checkpoint_key(checkpoint_id)
        cached = await cache_service.get(cache_key)
        if cached:
            return cached
        now = datetime.now(timezone.utc)
        try:
            row = (await db.execute(text("SELECT status, name FROM checkpoints WHERE id = :cid"), {"cid": checkpoint_id})).fetchone()
            current_status = row.status if row else "unknown"
            cp_name = row.name if row else f"Checkpoint {checkpoint_id}"
        except:
            current_status, cp_name = "unknown", f"Checkpoint {checkpoint_id}"
        total_score = (
            WEIGHT_HOUR_OF_DAY * _hour_risk(now.hour) +
            WEIGHT_DAY_OF_WEEK * _dow_risk(now.weekday())
        )
        result = {
            "checkpoint_id": checkpoint_id,
            "checkpoint_name": cp_name,
            "current_status": current_status,
            "predicted_status": _score_to_status(total_score),
            "risk_score": round(total_score, 3),
            "risk_level": _score_to_label(total_score),
            "factors": {"hour_of_day": now.hour, "day_of_week": now.strftime("%A")},
            "generated_at": now.isoformat(),
        }
        await cache_service.set(cache_key, result, ttl=TTL_PREDICTION)
        return result

    async def predict_region(self, region, db):
        cache_key = cache_service.prediction_region_key(region)
        cached = await cache_service.get(cache_key)
        if cached:
            return cached
        now = datetime.now(timezone.utc)
        try:
            rows = (await db.execute(text("SELECT status, COUNT(*) AS cnt FROM checkpoints WHERE LOWER(region)=LOWER(:r) GROUP BY status"), {"r": region})).fetchall()
            cp_stats = {row.status: row.cnt for row in rows}
        except:
            cp_stats = {}
        total = sum(cp_stats.values()) or 1
        closed = cp_stats.get("closed",0) + cp_stats.get("restricted",0)
        total_score = (
            WEIGHT_RECENT_CLOSURE * (closed/total) +
            WEIGHT_HOUR_OF_DAY * _hour_risk(now.hour) +
            WEIGHT_DAY_OF_WEEK * _dow_risk(now.weekday())
        )
        result = {
            "region": region,
            "risk_score": round(total_score, 3),
            "risk_level": _score_to_label(total_score),
            "checkpoint_summary": {"total": total, "closed": cp_stats.get("closed",0), "restricted": cp_stats.get("restricted",0), "open": cp_stats.get("open",0)},
            "generated_at": now.isoformat(),
        }
        await cache_service.set(cache_key, result, ttl=TTL_PREDICTION)
        return result

prediction_service = PredictionService()