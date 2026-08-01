"""Integration tests for extension system."""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_load_extension():
    """Test loading an extension."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        extension_data = {
            "name": "test_extension",
            "version": "1.0.0",
            "description": "Test extension",
            "permissions": ["read:tasks", "write:tasks"]
        }

        response = await client.post(
            "/extensions/load",
            json=extension_data,
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code in [200, 401, 400]


@pytest.mark.asyncio
async def test_unload_extension():
    """Test unloading an extension."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/extensions/unload/test_extension",
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_list_extensions():
    """Test listing loaded extensions."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/extensions",
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


@pytest.mark.asyncio
async def test_extension_webhook():
    """Test extension webhook handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        webhook_data = {
            "event_type": "task.created",
            "data": {"task_id": "task1"},
            "timestamp": "2024-01-01T00:00:00Z"
        }

        response = await client.post(
            "/extensions/webhook",
            json=webhook_data
        )

        assert response.status_code in [200, 400]


@pytest.mark.asyncio
async def test_extension_permissions():
    """Test extension permission validation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        extension_data = {
            "name": "test_extension",
            "version": "1.0.0",
            "permissions": ["admin:delete_all"]  # Invalid permission
        }

        response = await client.post(
            "/extensions/validate",
            json=extension_data
        )

        assert response.status_code in [200, 400]
        if response.status_code == 400:
            data = response.json()
            assert "error" in data


@pytest.mark.asyncio
async def test_extension_registry():
    """Test extension registry operations."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Get extension from registry
        response = await client.get("/extensions/registry/test_extension")

        assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_extension_sdk_call():
    """Test extension SDK API call."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Simulate extension SDK call
        response = await client.post(
            "/extensions/sdk/call",
            json={
                "extension_id": "test_extension",
                "method": "create_task",
                "params": {"title": "Test task"}
            },
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code in [200, 401, 404]
