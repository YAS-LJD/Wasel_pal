"""
routers/external.py — External API Endpoints
Person 4: Cache & Prediction & External APIs
"""

import logging
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config import settings
from app.core.dependencies import get_current_user
from app.services.cache_service import TTL_GEOCODE, cache_service
from app.services.weather_service import weather_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/external", tags=["External APIs"])

ORS_GEOCODE_URL = "https://api.openrouteservice.org/geocode/search"

@router.get("/weather/{region}")
async def get_weather(
    region: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        data = await weather_service.get_weather(region)
    except Exception as exc:
        logger.error(f"Weather endpoint error for '{region}': {exc}")
        raise HTTPException(status_code=503, detail="Weather service is currently unavailable.")
    return {"region": region, "weather": data}

@router.get("/geocode")
async def geocode_address(
    address: str = Query(...),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    cache_key = cache_service.geocode_key(address)
    cached = await cache_service.get(cache_key)
    if cached:
        return {**cached, "from_cache": True}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(ORS_GEOCODE_URL, params={"api_key": settings.OPENROUTESERVICE_API_KEY, "text": address, "size": 1})
            resp.raise_for_status()
            geo_data = resp.json()
    except Exception as exc:
        logger.error(f"Geocode error: {exc}")
        raise HTTPException(status_code=503, detail="Geocoding service is currently unavailable.")
    features = geo_data.get("features", [])
    if not features:
        raise HTTPException(status_code=404, detail=f"No location found for: '{address}'")
    coords = features[0]["geometry"]["coordinates"]
    props = features[0].get("properties", {})
    result = {"address": address, "latitude": coords[1], "longitude": coords[0], "label": props.get("label", address), "from_cache": False}
    await cache_service.set(cache_key, result, ttl=TTL_GEOCODE)
    return result
