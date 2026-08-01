"""Performance tests for API endpoints."""

import time

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_api_root_performance():
    """Test root endpoint performance."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        times = []

        for _ in range(10):
            start_time = time.time()
            response = await client.get("/")
            elapsed = time.time() - start_time
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        print(f"Root endpoint average response time: {avg_time * 1000:.2f}ms")
        assert avg_time < 0.1  # Should respond in under 100ms


@pytest.mark.asyncio
async def test_api_health_performance():
    """Test health endpoint performance."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        times = []

        for _ in range(10):
            start_time = time.time()
            response = await client.get("/health")
            elapsed = time.time() - start_time
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        print(f"Health endpoint average response time: {avg_time * 1000:.2f}ms")
        assert avg_time < 0.1  # Should respond in under 100ms


@pytest.mark.asyncio
async def test_api_concurrent_requests():
    """Test concurrent API requests."""
    import asyncio

    async def make_request():
        async with AsyncClient(app=app, base_url="http://test") as client:
            start_time = time.time()
            response = await client.get("/health")
            return time.time() - start_time

    start_time = time.time()

    # Make 50 concurrent requests
    times = await asyncio.gather(*[make_request() for _ in range(50)])

    elapsed = time.time() - start_time
    avg_time = sum(times) / len(times)

    print(f"50 concurrent requests total time: {elapsed * 1000:.2f}ms")
    print(f"Average response time: {avg_time * 1000:.2f}ms")
    assert elapsed < 5.0  # Should complete in under 5 seconds


@pytest.mark.asyncio
async def test_api_payload_size():
    """Test API performance with different payload sizes."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Small payload
        small_data = {"title": "Test"}
        start_time = time.time()
        await client.post("/tasks", json=small_data)
        small_time = time.time() - start_time

        # Medium payload
        medium_data = {"title": "Test", "description": "A" * 100}
        start_time = time.time()
        await client.post("/tasks", json=medium_data)
        medium_time = time.time() - start_time

        # Large payload
        large_data = {"title": "Test", "description": "A" * 1000}
        start_time = time.time()
        await client.post("/tasks", json=large_data)
        large_time = time.time() - start_time

        print(f"Small payload: {small_time * 1000:.2f}ms")
        print(f"Medium payload: {medium_time * 1000:.2f}ms")
        print(f"Large payload: {large_time * 1000:.2f}ms")

        assert large_time < 1.0  # Even large payloads should be fast


@pytest.mark.asyncio
async def test_api_rate_limiting():
    """Test API rate limiting performance."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make rapid requests to test rate limiting
        start_time = time.time()

        responses = []
        for _ in range(20):
            response = await client.get("/health")
            responses.append(response.status_code)

        elapsed = time.time() - start_time

        print(f"20 requests time: {elapsed * 1000:.2f}ms")
        print(f"Rate limited requests: {responses.count(429)}")

        assert elapsed < 2.0  # Should complete quickly
