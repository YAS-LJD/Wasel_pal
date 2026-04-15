import logging
import httpx
from app.config import settings
from app.services.cache_service import TTL_WEATHER, cache_service

logger = logging.getLogger(__name__)
OPENWEATHER_BASE = "https://api.openweathermap.org/data/2.5"


class WeatherService:
    async def _fetch(self, url, params):
        params["appid"] = settings.OPENWEATHER_API_KEY
        params["units"] = "metric"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    def _normalise(data):
        w = data.get("weather", [{}])
        m = data.get("main", {})
        return {
            "city": data.get("name", "unknown"),
            "condition": w[0].get("main", "Unknown"),
            "description": w[0].get("description", ""),
            "temperature": m.get("temp"),
            "humidity": m.get("humidity"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "timestamp": data.get("dt")
        }

    async def get_weather(self, region):
        cache_key = cache_service.weather_key(region)
        cached = await cache_service.get(cache_key)
        if cached:
            return cached
        try:
            raw = await self._fetch(
                f"{OPENWEATHER_BASE}/weather",
                {"q": f"{region},PS"}
            )
            result = self._normalise(raw)
        except Exception as exc:
            logger.error(f"WeatherService error: {exc}")
            return {
                "city": region,
                "condition": "unavailable",
                "description": "Weather service temporarily unavailable",
                "temperature": None,
                "humidity": None,
                "wind_speed": None,
                "timestamp": None
            }
        await cache_service.set(cache_key, result, ttl=TTL_WEATHER)
        return result


weather_service = WeatherService()