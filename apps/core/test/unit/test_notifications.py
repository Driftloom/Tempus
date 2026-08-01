"""Unit tests for notifications module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.notifications.scheduler.quiet_hours import QuietHoursManager
from app.notifications.scheduler.tasks import schedule_notification
from app.notifications.service import NotificationService


@pytest.fixture
def notification_service():
    """Create notification service fixture."""
    with patch('app.notifications.service.notification_repository') as mock_repo:
        return NotificationService(mock_repo)


@pytest.fixture
def quiet_hours_manager():
    """Create quiet hours manager fixture."""
    return QuietHoursManager()


# Notification Service Tests
@pytest.mark.asyncio
async def test_notification_service_create(notification_service):
    """Test notification creation."""
    notification_data = {
        "user_id": "user123",
        "type": "task_reminder",
        "message": "Task due in 1 hour",
        "channels": ["email", "push"]
    }

    with patch.object(notification_service.notification_repo, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = {"id": "notif1", **notification_data}

        result = await notification_service.create(notification_data)

        assert result["type"] == "task_reminder"


@pytest.mark.asyncio
async def test_notification_service_send(notification_service):
    """Test sending notification."""
    with patch.object(notification_service, '_send_email', new_callable=AsyncMock) as mock_email:
        with patch.object(notification_service, '_send_push', new_callable=AsyncMock) as mock_push:
            mock_email.return_value = True
            mock_push.return_value = True

            notification = {
                "id": "notif1",
                "user_id": "user123",
                "channels": ["email", "push"],
                "message": "Test message"
            }

            result = await notification_service.send(notification)

            assert result is True


@pytest.mark.asyncio
async def test_notification_service_get(notification_service):
    """Test notification retrieval."""
    with patch.object(notification_service.notification_repo, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"id": "notif1", "message": "Test"}

        result = await notification_service.get("notif1")

        assert result["id"] == "notif1"


@pytest.mark.asyncio
async def test_notification_service_list(notification_service):
    """Test notification listing."""
    with patch.object(notification_service.notification_repo, 'list', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = [
            {"id": "notif1", "message": "Test 1"},
            {"id": "notif2", "message": "Test 2"},
        ]

        result = await notification_service.list("user123")

        assert len(result) == 2


@pytest.mark.asyncio
async def test_notification_service_mark_read(notification_service):
    """Test marking notification as read."""
    with patch.object(notification_service.notification_repo, 'update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = {"id": "notif1", "read": True}

        result = await notification_service.mark_read("notif1")

        assert result["read"] is True


# Quiet Hours Manager Tests
def test_quiet_hours_manager_initialization(quiet_hours_manager):
    """Test quiet hours manager initialization."""
    assert quiet_hours_manager is not None


def test_quiet_hours_manager_set_quiet_hours(quiet_hours_manager):
    """Test setting quiet hours."""
    quiet_hours_manager.set_quiet_hours("user123", "22:00", "08:00")

    assert "user123" in quiet_hours_manager.quiet_hours


def test_quiet_hours_manager_is_quiet_hours(quiet_hours_manager):
    """Test checking if in quiet hours."""
    from datetime import time

    quiet_hours_manager.set_quiet_hours("user123", "22:00", "08:00")

    # Test at 23:00 (should be quiet)
    is_quiet = quiet_hours_manager.is_quiet_hours("user123", time(23, 0))
    assert is_quiet is True

    # Test at 10:00 (should not be quiet)
    is_quiet = quiet_hours_manager.is_quiet_hours("user123", time(10, 0))
    assert is_quiet is False


def test_quiet_hours_manager_get_next_notification_time(quiet_hours_manager):
    """Test getting next notification time."""
    from datetime import time

    quiet_hours_manager.set_quiet_hours("user123", "22:00", "08:00")

    next_time = quiet_hours_manager.get_next_notification_time("user123", time(23, 0))

    assert next_time is not None


# Notification Scheduler Tests
@pytest.mark.asyncio
async def test_schedule_notification():
    """Test scheduling notification."""
    notification_data = {
        "user_id": "user123",
        "scheduled_time": "2024-01-01T10:00:00Z",
        "message": "Test notification"
    }

    with patch('app.notifications.scheduler.tasks.NotificationService') as mock_service:
        mock_service_instance = MagicMock()
        mock_service_instance.create = AsyncMock(return_value={"id": "notif1"})
        mock_service.return_value = mock_service_instance

        result = await schedule_notification(notification_data)

        assert result is not None


@pytest.mark.asyncio
async def test_schedule_notification_with_quiet_hours():
    """Test scheduling notification with quiet hours."""

    notification_data = {
        "user_id": "user123",
        "scheduled_time": "2024-01-01T23:00:00Z",  # During quiet hours
        "message": "Test notification"
    }

    with patch('app.notifications.scheduler.tasks.QuietHoursManager') as mock_qh:
        mock_qh_instance = MagicMock()
        mock_qh_instance.is_quiet_hours.return_value = True
        mock_qh_instance.get_next_notification_time.return_value = "2024-01-02T08:00:00Z"
        mock_qh.return_value = mock_qh_instance

        with patch('app.notifications.scheduler.tasks.NotificationService') as mock_service:
            mock_service_instance = MagicMock()
            mock_service_instance.create = AsyncMock(return_value={"id": "notif1"})
            mock_service.return_value = mock_service_instance

            result = await schedule_notification(notification_data)

            assert result is not None
