"""Redis client configuration."""

import redis.asyncio as redis
from app.core.config import settings
import structlog

logger = structlog.get_logger(__name__)


class RedisClient:
    """Redis client wrapper for async operations."""

    def __init__(self):
        """Initialize Redis client."""
        self.client = None

    async def connect(self):
        """Connect to Redis."""
        self.client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )
        logger.info("Redis client connected")

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
            logger.info("Redis client disconnected")

    async def ping(self) -> bool:
        """Check Redis connection."""
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error("Redis ping failed", error=str(e))
            return False

    async def get(self, key: str) -> str | None:
        """Get value from Redis."""
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error("Redis get failed", key=key, error=str(e))
            return None

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        """Set value in Redis with optional expiration."""
        try:
            return await self.client.set(key, value, ex=ex)
        except Exception as e:
            logger.error("Redis set failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            return await self.client.delete(key) > 0
        except Exception as e:
            logger.error("Redis delete failed", key=key, error=str(e))
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern."""
        try:
            keys = await self.client.keys(pattern)
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error("Redis delete pattern failed", pattern=pattern, error=str(e))
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error("Redis exists failed", key=key, error=str(e))
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key."""
        try:
            return await self.client.expire(key, seconds)
        except Exception as e:
            logger.error("Redis expire failed", key=key, error=str(e))
            return False

    async def ttl(self, key: str) -> int:
        """Get time to live for key."""
        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.error("Redis ttl failed", key=key, error=str(e))
            return -1


# Global Redis client instance
redis_client = RedisClient()
