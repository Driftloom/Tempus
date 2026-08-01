"""Unit tests for cache service."""

from unittest.mock import AsyncMock

import pytest

from app.cache.cache_service import CacheService


@pytest.fixture
def cache_service():
    """Create cache service fixture."""
    return CacheService(prefix="test")


@pytest.fixture
def mock_redis_client():
    """Create mock Redis client."""
    client = AsyncMock()
    client.get = AsyncMock(return_value='{"key": "value"}')
    client.set = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=True)
    client.delete_pattern = AsyncMock(return_value=2)
    client.exists = AsyncMock(return_value=True)
    client.expire = AsyncMock(return_value=True)
    client.ttl = AsyncMock(return_value=3600)
    return client


@pytest.mark.asyncio
async def test_cache_get(cache_service, mock_redis_client):
    """Test cache get operation."""
    cache_service.redis_client = mock_redis_client

    result = await cache_service.get("test_key")

    assert result == {"key": "value"}
    mock_redis_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_cache_set(cache_service, mock_redis_client):
    """Test cache set operation."""
    cache_service.redis_client = mock_redis_client

    result = await cache_service.set("test_key", {"data": "value"}, ttl=60)

    assert result is True
    mock_redis_client.set.assert_called_once()


@pytest.mark.asyncio
async def test_cache_delete(cache_service, mock_redis_client):
    """Test cache delete operation."""
    cache_service.redis_client = mock_redis_client

    result = await cache_service.delete("test_key")

    assert result is True
    mock_redis_client.delete.assert_called_once()


@pytest.mark.asyncio
async def test_cache_invalidate_pattern(cache_service, mock_redis_client):
    """Test cache pattern invalidation."""
    cache_service.redis_client = mock_redis_client

    result = await cache_service.invalidate_pattern("user:*")

    assert result == 2
    mock_redis_client.delete_pattern.assert_called_once()


@pytest.mark.asyncio
async def test_cache_get_or_set_miss(cache_service, mock_redis_client):
    """Test cache get_or_set on cache miss."""
    cache_service.redis_client = mock_redis_client
    mock_redis_client.get = AsyncMock(return_value=None)

    fetch_fn = AsyncMock(return_value={"fetched": "data"})

    result = await cache_service.get_or_set("test_key", fetch_fn)

    assert result == {"fetched": "data"}
    fetch_fn.assert_called_once()
    mock_redis_client.set.assert_called_once()


@pytest.mark.asyncio
async def test_cache_get_or_set_hit(cache_service, mock_redis_client):
    """Test cache get_or_set on cache hit."""
    cache_service.redis_client = mock_redis_client

    fetch_fn = AsyncMock(return_value={"fetched": "data"})

    result = await cache_service.get_or_set("test_key", fetch_fn)

    assert result == {"key": "value"}
    fetch_fn.assert_not_called()
