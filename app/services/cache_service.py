import json
import logging
from typing import Any, Optional
import redis.asyncio as aioredis
from app.config import settings

logger = logging.getLogger(__name__)

TTL_WEATHER = 1800
TTL_ROUTES = 300
TTL_STATS = 600
TTL_CHECKPOINTS = 120
TTL_PREDICTION = 900
TTL_GEOCODE = 3600

class CacheService:
    def __init__(self):
        self._redis = None

    async def connect(self):
        try:
            self._redis = aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                encoding="utf-8",
                decode_responses=True,
            )
            await self._redis.ping()
            logger.info("Redis connected successfully")
        except Exception as exc:
            logger.warning(f"Redis connection failed: {exc}")
            self._redis = None

    async def close(self):
        if self._redis:
            await self._redis.close()

    async def get(self, key):
        if not self._redis:
            return None
        try:
            raw = await self._redis.get(key)
            return json.loads(raw) if raw else None
        except Exception:
            return None

    async def set(self, key, value, ttl=600):
        if not self._redis:
            return False
        try:
            await self._redis.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception:
            return False

    async def delete(self, key):
        if not self._redis:
            return False
        try:
            return bool(await self._redis.delete(key))
        except Exception:
            return False

    @staticmethod
    def weather_key(region):
        return f"weather:{region.lower()}"

    @staticmethod
    def geocode_key(address):
        return f"geocode:{address.strip().lower()}"

    @staticmethod
    def checkpoint_list_key(region=None):
        return f"checkpoints:list:{region.lower() if region else 'all'}"

    @staticmethod
    def stats_checkpoints_key():
        return "stats:checkpoints"

    @staticmethod
    def prediction_checkpoint_key(checkpoint_id):
        return f"predict:checkpoint:{checkpoint_id}"

    @staticmethod
    def prediction_region_key(region):
        return f"predict:region:{region.lower()}"

cache_service = CacheService()
