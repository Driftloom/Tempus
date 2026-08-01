"""Cache decorators for easy caching."""

from collections.abc import Callable
from functools import wraps

import structlog

from app.cache.cache_service import cache_service

logger = structlog.get_logger(__name__)


def cached(
    key_prefix: str,
    ttl: int | None = None,
    hash_key: bool = False,
    invalidate_on: list[str] | None = None,
):
    """Decorator to cache function results."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix]

            # Add user_id if present
            if "user_id" in kwargs:
                key_parts.append(f"user:{kwargs['user_id']}")
            elif len(args) > 0:
                key_parts.append(f"user:{args[0]}")

            # Add other identifying parameters
            for k, v in sorted(kwargs.items()):
                if k != "user_id" and k not in ("db", "session"):
                    key_parts.append(f"{k}:{v}")

            cache_key = ":".join(key_parts)

            # Try to get from cache
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                logger.debug("Cache hit", key=cache_key)
                return cached_value

            # Execute function
            logger.debug("Cache miss", key=cache_key)
            result = await func(*args, **kwargs)

            # Cache result
            if result is not None:
                await cache_service.set(cache_key, result, ttl=ttl, hash_key=hash_key)

            return result

        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """Decorator to invalidate cache after function execution."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            # Invalidate cache pattern
            if "user_id" in kwargs:
                pattern_with_user = pattern.format(user_id=kwargs["user_id"])
                await cache_service.invalidate_pattern(pattern_with_user)
            elif len(args) > 0:
                pattern_with_user = pattern.format(user_id=args[0])
                await cache_service.invalidate_pattern(pattern_with_user)

            return result

        return wrapper
    return decorator


def cache_user_data(ttl: int = 3600):
    """Decorator to cache user-specific data."""
    return cached("user_data", ttl=ttl)


def cache_tasks(ttl: int = 300):
    """Decorator to cache task data (short TTL)."""
    return cached("tasks", ttl=ttl)


def cache_memory(ttl: int = 600):
    """Decorator to cache memory data (medium TTL)."""
    return cached("memory", ttl=ttl)


def cache_connectors(ttl: int = 1800):
    """Decorator to cache connector data."""
    return cached("connectors", ttl=ttl)
