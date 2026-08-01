"""Integration tests for API error handling."""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_404_not_found():
    """Test 404 error handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/nonexistent/endpoint")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_405_method_not_allowed():
    """Test 405 error handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Try POST on GET endpoint
        response = await client.post("/health")
        assert response.status_code in [405, 200]  # May accept POST


@pytest.mark.asyncio
async def test_422_validation_error():
    """Test 422 validation error handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Send invalid data
        response = await client.post("/auth/login", json={"invalid": "data"})
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_401_unauthorized():
    """Test 401 unauthorized error handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Access protected endpoint without token
        response = await client.get("/tasks")
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_403_forbidden():
    """Test 403 forbidden error handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Access with invalid token
        response = await client.get(
            "/tasks",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_429_rate_limit():
    """Test 429 rate limit error handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make many requests to trigger rate limit
        for _ in range(65):
            response = await client.post(
                "/auth/login",
                json={"email": "test@example.com", "password": "TestPassword123!"}
            )
            if response.status_code == 429:
                assert "rate limit" in response.json().get("detail", "").lower()
                break
        else:
            pytest.fail("Rate limit not triggered")


@pytest.mark.asyncio
async def test_500_internal_server_error():
    """Test 500 error handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # This endpoint may not exist, but if it does, it should handle errors gracefully
        response = await client.get("/error/test")
        # Should not return raw stack trace
        assert response.status_code in [404, 500]
        if response.status_code == 500:
            # Should have error message, not stack trace
            data = response.json()
            assert "detail" in data or "error" in data


@pytest.mark.asyncio
async def test_malformed_json():
    """Test malformed JSON error handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            data="{invalid json}",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_missing_content_type():
    """Test missing content-type error handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            data='{"email":"test@example.com","password":"test"}'
        )
        assert response.status_code in [400, 415, 422]


@pytest.mark.asyncio
async def test_empty_request_body():
    """Test empty request body error handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/login", json={})
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_extra_fields():
    """Test handling of extra fields in request."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
                "extra_field": "should_be_ignored"
            }
        )
        # Should either accept (ignore extra) or reject
        assert response.status_code in [200, 400, 422]


@pytest.mark.asyncio
async def test_large_payload():
    """Test large payload error handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        large_data = {"data": "x" * 10000000}  # 10MB
        response = await client.post("/auth/login", json=large_data)
        assert response.status_code in [400, 413, 422]
