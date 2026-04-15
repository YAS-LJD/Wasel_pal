"""
routers/external.py — External API Endpoints
Person 4: Cache & Prediction & External APIs

Endpoints
---------
GET /api/v1/external/weather/{region}   → weather for a Palestinian region
GET /api/v1/external/geocode            → address → lat/lng via OpenRouteService
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


# ── GET /external/weather/{region} ────────────────────────────────────────
@router.get(
    "/weather/{region}",
    summary="Get current weather for a region",
    response_description="Current weather conditions",
)
async def get_weather(
    region: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Returns current weather data for the given Palestinian region.

    - Results are **cached for 30 minutes**.
    - Requires authentication.
    - `region` examples: `Ramallah`, `Nablus`, `Hebron`, `Jenin`, `Gaza`
    """
    try:
        data = await weather_service.get_weather(region)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Weather service API key is invalid or missing.",
            )
        if exc.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Region '{region}' not found in weather service.",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Weather service returned an unexpected error.",
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Weather service request timed out.",
        )
    except Exception as exc:
        logger.error(f"Weather endpoint error for '{region}': {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weather service is currently unavailable.",
        )

    return {
        "region":  region,
        "weather": data,
        "cached":  False,   # cache hit/miss is transparent to clients
    }


# ── GET /external/geocode ─────────────────────────────────────────────────
@router.get(
    "/geocode",
    summary="Convert address to coordinates",
    response_description="Latitude and longitude for the given address",
)
async def geocode_address(
    address: str = Query(..., description="Street address or place name to geocode"),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Converts a Palestinian address or place name to geographic coordinates
    using the **OpenRouteService Geocoding API**.

    - Results are **cached for 1 hour** (addresses rarely change).
    - Requires authentication.

    **Example:** `?address=Ramallah City Center`
    """
    cache_key = cache_service.geocode_key(address)
    cached = await cache_service.get(cache_key)
    if cached:
        return {**cached, "from_cache": True}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                ORS_GEOCODE_URL,
                params={
                    "api_key": settings.OPENROUTESERVICE_API_KEY,
                    "text":    address,
                    "size":    1,
                    # Bias results toward Palestine bounding box
                    "boundary.rect.min_lon": 34.2,
                    "boundary.rect.min_lat": 29.4,
                    "boundary.rect.max_lon": 35.7,
                    "boundary.rect.max_lat": 33.4,
                },
            )
            resp.raise_for_status()
            geo_data = resp.json()

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Geocoding service API key is invalid or missing.",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Geocoding service returned an unexpected error.",
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Geocoding service request timed out.",
        )
    except Exception as exc:
        logger.error(f"Geocode endpoint error for '{address}': {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Geocoding service is currently unavailable.",
        )

    features = geo_data.get("features", [])
    if not features:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No location found for address: '{address}'",
        )

    feature    = features[0]
    coords     = feature["geometry"]["coordinates"]   # [lng, lat]
    properties = feature.get("properties", {})

    result = {
        "address":      address,
        "latitude":     coords[1],
        "longitude":    coords[0],
        "label":        properties.get("label", address),
        "confidence":   properties.get("confidence", None),
        "country":      properties.get("country", None),
        "region":       properties.get("region", None),
        "locality":     properties.get("locality", None),
        "from_cache":   False,
    }

    await cache_service.set(cache_key, result, ttl=TTL_GEOCODE)
    return result