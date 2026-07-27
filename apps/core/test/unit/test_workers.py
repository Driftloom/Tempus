"""Unit tests for workers module."""

import pytest
from unittest.mock import AsyncMock, patch
from app.workers.celery_app import celery_app
from app.workers.tasks.agent_tasks import process_agent_task
from app.workers.tasks.email_tasks import process_email_task
from app.workers.tasks.memory_tasks import process_memory_task
from app.workers.tasks.notification_tasks import send_notification_task


@pytest.fixture
def mock_celery():
    """Create mock Celery app."""
    with patch('app.workers.celery_app.Celery') as mock_celery:
        mock_app = MagicMock()
        mock_celery.return_value = mock_app
        return mock_app


# Celery App Tests
def test_celery_app_initialization():
    """Test Celery app initialization."""
    assert celery_app is not None
    assert celery_app.name == "tempus_workers"


def test_celery_app_broker_config():
    """Test Celery broker configuration."""
    assert celery_app.conf.broker_url is not None


def test_celery_app_backend_config():
    """Test Celery backend configuration."""
    assert celery_app.conf.result_backend is not None


# Agent Tasks Tests
@pytest.mark.asyncio
async def test_process_agent_task():
    """Test processing agent task."""
    task_data = {
        "agent_id": "agent1",
        "user_id": "user123",
        "goal": "Test goal",
    }
    
    with patch('app.workers.tasks.agent_tasks.AgentBase') as mock_agent:
        mock_agent_instance = MagicMock()
        mock_agent_instance.execute = AsyncMock(return_value={"result": "success"})
        mock_agent.return_value = mock_agent_instance
        
        result = await process_agent_task(task_data)
        
        assert result is not None


@pytest.mark.asyncio
async def test_process_agent_task_with_error():
    """Test processing agent task with error."""
    task_data = {
        "agent_id": "agent1",
        "user_id": "user123",
        "goal": "Test goal",
    }
    
    with patch('app.workers.tasks.agent_tasks.AgentBase') as mock_agent:
        mock_agent_instance = MagicMock()
        mock_agent_instance.execute = AsyncMock(side_effect=Exception("Test error"))
        mock_agent.return_value = mock_agent_instance
        
        with pytest.raises(Exception):
            await process_agent_task(task_data)


# Email Tasks Tests
@pytest.mark.asyncio
async def test_process_email_task():
    """Test processing email task."""
    task_data = {
        "email_id": "email1",
        "user_id": "user123",
        "subject": "Test email",
        "body": "Test body",
    }
    
    with patch('app.workers.tasks.email_tasks.EmailProcessor') as mock_processor:
        mock_processor_instance = MagicMock()
        mock_processor_instance.process = AsyncMock(return_value={"tasks": ["task1"]})
        mock_processor.return_value = mock_processor_instance
        
        result = await process_email_task(task_data)
        
        assert result is not None


@pytest.mark.asyncio
async def test_process_email_task_extraction():
    """Test email task extraction."""
    task_data = {
        "email_id": "email1",
        "user_id": "user123",
        "subject": "Meeting tomorrow at 3PM",
        "body": "Don't forget the meeting",
    }
    
    with patch('app.workers.tasks.email_tasks.EmailProcessor') as mock_processor:
        mock_processor_instance = MagicMock()
        mock_processor_instance.process = AsyncMock(return_value={"tasks": [{"title": "Meeting at 3PM"}]})
        mock_processor.return_value = mock_processor_instance
        
        result = await process_email_task(task_data)
        
        assert "tasks" in result


# Memory Tasks Tests
@pytest.mark.asyncio
async def test_process_memory_task():
    """Test processing memory task."""
    task_data = {
        "memory_id": "mem1",
        "user_id": "user123",
        "content": "Test memory content",
    }
    
    with patch('app.workers.tasks.memory_tasks.MemoryService') as mock_service:
        mock_service_instance = MagicMock()
        mock_service_instance.process_memory = AsyncMock(return_value={"embedding": [0.1, 0.2, 0.3]})
        mock_service.return_value = mock_service_instance
        
        result = await process_memory_task(task_data)
        
        assert result is not None


@pytest.mark.asyncio
async def test_process_memory_task_embedding():
    """Test memory embedding generation."""
    task_data = {
        "memory_id": "mem1",
        "user_id": "user123",
        "content": "Test memory content",
    }
    
    with patch('app.workers.tasks.memory_tasks.MemoryService') as mock_service:
        mock_service_instance = MagicMock()
        mock_service_instance.process_memory = AsyncMock(return_value={"embedding": [0.1, 0.2, 0.3]})
        mock_service.return_value = mock_service_instance
        
        result = await process_memory_task(task_data)
        
        assert "embedding" in result


# Notification Tasks Tests
@pytest.mark.asyncio
async def test_send_notification_task():
    """Test sending notification task."""
    task_data = {
        "user_id": "user123",
        "type": "task_reminder",
        "message": "Task due in 1 hour",
    }
    
    with patch('app.workers.tasks.notification_tasks.NotificationService') as mock_service:
        mock_service_instance = MagicMock()
        mock_service_instance.send = AsyncMock(return_value={"sent": True})
        mock_service.return_value = mock_service_instance
        
        result = await send_notification_task(task_data)
        
        assert result.get("sent") is True


@pytest.mark.asyncio
async def test_send_notification_task_with_channels():
    """Test sending notification with multiple channels."""
    task_data = {
        "user_id": "user123",
        "type": "task_reminder",
        "message": "Task due in 1 hour",
        "channels": ["email", "push"],
    }
    
    with patch('app.workers.tasks.notification_tasks.NotificationService') as mock_service:
        mock_service_instance = MagicMock()
        mock_service_instance.send = AsyncMock(return_value={"sent": True, "channels": ["email", "push"]})
        mock_service.return_value = mock_service_instance
        
        result = await send_notification_task(task_data)
        
        assert "channels" in result
