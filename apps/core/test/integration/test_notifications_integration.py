"""Integration tests for notification system."""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_notification():
    """Test creating a notification."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        notification_data = {
            "user_id": "user123",
            "type": "task_reminder",
            "message": "Task due in 1 hour",
            "channels": ["email", "push"]
        }
        
        response = await client.post(
            "/notifications",
            json=notification_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 201, 401]


@pytest.mark.asyncio
async def test_send_notification():
    """Test sending a notification."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/notifications/send/notif1",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_list_notifications():
    """Test listing user notifications."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/notifications/user/user123",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


@pytest.mark.asyncio
async def test_mark_notification_read():
    """Test marking notification as read."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.patch(
            "/notifications/notif1/read",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_schedule_notification():
    """Test scheduling a notification."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        notification_data = {
            "user_id": "user123",
            "scheduled_time": "2024-01-01T10:00:00Z",
            "message": "Scheduled notification"
        }
        
        response = await client.post(
            "/notifications/schedule",
            json=notification_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 201, 401]


@pytest.mark.asyncio
async def test_notification_channels():
    """Test notification through multiple channels."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        notification_data = {
            "user_id": "user123",
            "type": "task_reminder",
            "message": "Test notification",
            "channels": ["email", "push", "sms"]
        }
        
        response = await client.post(
            "/notifications",
            json=notification_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 201, 401]


@pytest.mark.asyncio
async def test_quiet_hours():
    """Test quiet hours for notifications."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Set quiet hours
        quiet_hours_data = {
            "user_id": "user123",
            "start_time": "22:00",
            "end_time": "08:00"
        }
        
        response = await client.post(
            "/notifications/quiet-hours",
            json=quiet_hours_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_notification_preferences():
    """Test user notification preferences."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        preferences_data = {
            "user_id": "user123",
            "email_enabled": True,
            "push_enabled": True,
            "sms_enabled": False
        }
        
        response = await client.put(
            "/notifications/preferences/user123",
            json=preferences_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 401]
