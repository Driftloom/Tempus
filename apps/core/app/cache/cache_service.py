"""Cache service with strategy and invalidation."""

from typing import Optional, Any, Callable
import json
import hashlib
from app.cache.redis_client import redis_client
import structlog

logger = structlog.get_logger(__name__)


class CacheService:
    """Cache service with strategy and invalidation."""

    def __init__(self, prefix: str = "tempus"):
        """Initialize cache service."""
        self.prefix = prefix
        self.default_ttl = 3600  # 1 hour

    def _make_key(self, *parts: str) -> str:
        """Create cache key from parts."""
        key = ":".join(str(part) for part in parts)
        return f"{self.prefix}:{key}"

    def _hash_key(self, *parts: str) -> str:
        """Create hashed cache key for long keys."""
        key = self._make_key(*parts)
        return hashlib.sha256(key.encode()).hexdigest()[:32]

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        cache_key = self._make_key(key)
        value = await redis_client.get(cache_key)
        
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        hash_key: bool = False
    ) -> bool:
        """Set value in cache."""
        cache_key = self._hash_key(key) if hash_key else self._make_key(key)
        ttl = ttl or self.default_ttl
        
        try:
            serialized = json.dumps(value) if not isinstance(value, str) else value
            return await redis_client.set(cache_key, serialized, ex=ttl)
        except (TypeError, ValueError) as e:
            logger.error("Cache serialization failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        cache_key = self._make_key(key)
        return await redis_client.delete(cache_key)

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        cache_pattern = self._make_key(pattern)
        return await redis_client.delete_pattern(f"{cache_pattern}*")

    async def get_or_set(
        self,
        key: str,
        fetch_fn: Callable,
        ttl: Optional[int] = None,
        hash_key: bool = False
    ) -> Any:
        """Get from cache or set using fetch function."""
        value = await self.get(key)
        
        if value is None:
            value = await fetch_fn()
            if value is not None:
                await self.set(key, value, ttl=ttl, hash_key=hash_key)
        
        return value

    async def invalidate_user_cache(self, user_id: str) -> int:
        """Invalidate all cache for a user."""
        return await self.invalidate_pattern(f"user:{user_id}")

    async def invalidate_memory_cache(self, user_id: str, memory_id: Optional[str] = None) -> int:
        """Invalidate memory cache."""
        if memory_id:
            return await self.delete(f"memory:{user_id}:{memory_id}")
        return await self.invalidate_pattern(f"memory:{user_id}")

    async def invalidate_task_cache(self, user_id: str, task_id: Optional[str] = None) -> int:
        """Invalidate task cache."""
        if task_id:
            return await self.delete(f"task:{user_id}:{task_id}")
        return await self.invalidate_pattern(f"task:{user_id}")

    async def invalidate_connector_cache(self, user_id: str, connector_id: Optional[str] = None) -> int:
        """Invalidate connector cache."""
        if connector_id:
            return await self.delete(f"connector:{user_id}:{connector_id}")
        return await self.invalidate_pattern(f"connector:{user_id}")


# Global cache service instance
cache_service = CacheService()
