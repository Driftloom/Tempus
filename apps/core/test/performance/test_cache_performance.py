"""Performance tests for cache operations."""

import asyncio

import pytest

from app.cache.cache_service import CacheService


@pytest.fixture
async def cache_service():
    """Create cache service with real Redis connection."""
    from app.cache.redis_client import redis_client
    await redis_client.connect()

    service = CacheService(prefix="perf_test")
    yield service

    await redis_client.disconnect()


@pytest.mark.asyncio
async def test_cache_set_performance(cache_service):
    """Test cache set performance."""
    import time

    iterations = 100
    start_time = time.time()

    for i in range(iterations):
        await cache_service.set(f"perf_key_{i}", {"data": f"value_{i}"}, ttl=60)

    elapsed = time.time() - start_time
    avg_time = elapsed / iterations

    print(f"Average cache set time: {avg_time * 1000:.2f}ms")
    assert avg_time < 0.01  # Should be under 10ms per operation


@pytest.mark.asyncio
async def test_cache_get_performance(cache_service):
    """Test cache get performance."""
    import time

    # Pre-populate cache
    for i in range(100):
        await cache_service.set(f"perf_key_{i}", {"data": f"value_{i}"}, ttl=60)

    iterations = 100
    start_time = time.time()

    for i in range(iterations):
        await cache_service.get(f"perf_key_{i}")

    elapsed = time.time() - start_time
    avg_time = elapsed / iterations

    print(f"Average cache get time: {avg_time * 1000:.2f}ms")
    assert avg_time < 0.01  # Should be under 10ms per operation


@pytest.mark.asyncio
async def test_cache_concurrent_operations(cache_service):
    """Test concurrent cache operations."""
    import time

    async def set_operation(i):
        await cache_service.set(f"concurrent_key_{i}", {"data": f"value_{i}"}, ttl=60)

    start_time = time.time()

    await asyncio.gather(*[set_operation(i) for i in range(50)])

    elapsed = time.time() - start_time
    print(f"Concurrent set operations time: {elapsed * 1000:.2f}ms for 50 operations")
    assert elapsed < 1.0  # Should complete in under 1 second
