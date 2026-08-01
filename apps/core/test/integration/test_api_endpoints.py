"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TEMPUS Core"
    assert data["status"] == "operational"


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data


@pytest.mark.asyncio
async def test_cors_headers():
    """Test CORS headers."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.options("/", headers={"Origin": "chrome-extension://test"})

    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
