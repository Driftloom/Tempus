"""Response cache for LLM responses."""

import json

import redis.asyncio as redis
from structlog import get_logger

from app.core.config import settings

logger = get_logger(__name__)


class ResponseCache:
    """Cache for LLM responses."""

    def __init__(self):
        """Initialize response cache."""
        self.redis_url = settings.redis_url
        self.redis_client = None

    async def _get_redis(self):
        """Get Redis client (lazy initialization)."""
        if not self.redis_client:
            self.redis_client = await redis.from_url(self.redis_url, decode_responses=True)
        return self.redis_client

    async def get(self, cache_key: str) -> dict | None:
        """Get cached response."""
        try:
            redis = await self._get_redis()
            cached = await redis.get(cache_key)
            if cached:
                logger.info("Cache hit", cache_key=cache_key)
                return json.loads(cached)
            return None
        except Exception as e:
            logger.error("Cache get failed", error=str(e))
            return None

    async def set(self, cache_key: str, response: dict, ttl: int = 3600) -> None:
        """Cache response with TTL."""
        try:
            redis = await self._get_redis()
            await redis.setex(cache_key, ttl, json.dumps(response))
            logger.info("Response cached", cache_key=cache_key, ttl=ttl)
        except Exception as e:
            logger.error("Cache set failed", error=str(e))

    async def invalidate(self, cache_key: str) -> None:
        """Invalidate cached response."""
        try:
            redis = await self._get_redis()
            await redis.delete(cache_key)
            logger.info("Cache invalidated", cache_key=cache_key)
        except Exception as e:
            logger.error("Cache invalidation failed", error=str(e))
