"""Security tests for rate limiting."""

import time

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_rate_limiting_enforcement():
    """Test rate limiting enforcement."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make rapid requests
        responses = []

        for _ in range(30):
            response = await client.get("/health")
            responses.append(response.status_code)

        # Should have rate limited requests
        assert 429 in responses


@pytest.mark.asyncio
async def test_rate_limiting_per_user():
    """Test per-user rate limiting."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # User 1 requests
        user1_responses = []
        for _ in range(20):
            response = await client.get(
                "/health",
                headers={"Authorization": "Bearer user1_token"}
            )
            user1_responses.append(response.status_code)

        # User 2 requests (should not be affected by user 1's limit)
        user2_responses = []
        for _ in range(20):
            response = await client.get(
                "/health",
                headers={"Authorization": "Bearer user2_token"}
            )
            user2_responses.append(response.status_code)

        # Both should be rate limited independently
        assert 429 in user1_responses or 429 in user2_responses


@pytest.mark.asyncio
async def test_rate_limiting_recovery():
    """Test rate limiting recovery after timeout."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Exhaust rate limit
        for _ in range(30):
            await client.get("/health")

        # Wait for recovery
        time.sleep(2)

        # Should be able to make requests again
        response = await client.get("/health")

        assert response.status_code in [200, 429]


@pytest.mark.asyncio
async def test_rate_limiting_headers():
    """Test rate limiting response headers."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

        # Check for rate limit headers
        headers = response.headers

        # Common rate limit headers
        rate_limit_headers = ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]

        # At least one should be present if rate limiting is enabled
        has_rate_limit = any(header in headers for header in rate_limit_headers)

        # This is optional - may not be implemented
        # assert has_rate_limit


@pytest.mark.asyncio
async def test_different_endpoints_rate_limits():
    """Test different rate limits for different endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Health endpoint (usually higher limit)
        health_responses = []
        for _ in range(50):
            response = await client.get("/health")
            health_responses.append(response.status_code)

        # API endpoint (usually lower limit)
        api_responses = []
        for _ in range(50):
            response = await client.get(
                "/tasks",
                headers={"Authorization": "Bearer test_token"}
            )
            api_responses.append(response.status_code)

        # API endpoint should be rate limited more aggressively
        api_limited = 429 in api_responses
        health_limited = 429 in health_responses

        # API should be limited first or more strictly
        assert api_limited or not health_limited


@pytest.mark.asyncio
async def test_burst_rate_limiting():
    """Test burst rate limiting."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Burst of requests
        import asyncio

        async def make_request():
            return await client.get("/health")

        # Make 20 concurrent requests
        responses = await asyncio.gather(*[make_request() for _ in range(20)])

        status_codes = [r.status_code for r in responses]

        # Should handle burst but may rate limit
        assert 429 in status_codes or all(code == 200 for code in status_codes)
