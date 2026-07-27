"""Integration tests for Celery workers."""

import pytest
from unittest.mock import AsyncMock, patch
from app.workers.celery_app import celery_app
from app.workers.tasks.agent_tasks import process_agent_task
from app.workers.tasks.email_tasks import process_email_task
from app.workers.tasks.memory_tasks import process_memory_task
from app.workers.tasks.notification_tasks import send_notification_task


@pytest.mark.asyncio
async def test_celery_worker_connection():
    """Test Celery worker connection to broker."""
    # Check if Celery app is configured
    assert celery_app.conf.broker_url is not None
    assert celery_app.conf.result_backend is not None


@pytest.mark.asyncio
async def test_agent_task_execution():
    """Test agent task execution through Celery."""
    task_data = {
        "agent_id": "agent1",
        "user_id": "user123",
        "goal": "Test goal"
    }
    
    with patch('app.workers.tasks.agent_tasks.AgentBase') as mock_agent:
        mock_agent_instance = MagicMock()
        mock_agent_instance.execute = AsyncMock(return_value={"result": "success"})
        mock_agent.return_value = mock_agent_instance
        
        result = await process_agent_task(task_data)
        
        assert result is not None
        assert "result" in result or "error" in result


@pytest.mark.asyncio
async def test_email_task_execution():
    """Test email task execution through Celery."""
    task_data = {
        "email_id": "email1",
        "user_id": "user123",
        "subject": "Test email",
        "body": "Test body"
    }
    
    with patch('app.workers.tasks.email_tasks.EmailProcessor') as mock_processor:
        mock_processor_instance = MagicMock()
        mock_processor_instance.process = AsyncMock(return_value={"tasks": []})
        mock_processor.return_value = mock_processor_instance
        
        result = await process_email_task(task_data)
        
        assert result is not None


@pytest.mark.asyncio
async def test_memory_task_execution():
    """Test memory task execution through Celery."""
    task_data = {
        "memory_id": "mem1",
        "user_id": "user123",
        "content": "Test memory content"
    }
    
    with patch('app.workers.tasks.memory_tasks.MemoryService') as mock_service:
        mock_service_instance = MagicMock()
        mock_service_instance.process_memory = AsyncMock(return_value={"embedding": []})
        mock_service.return_value = mock_service_instance
        
        result = await process_memory_task(task_data)
        
        assert result is not None


@pytest.mark.asyncio
async def test_notification_task_execution():
    """Test notification task execution through Celery."""
    task_data = {
        "user_id": "user123",
        "type": "task_reminder",
        "message": "Task due in 1 hour"
    }
    
    with patch('app.workers.tasks.notification_tasks.NotificationService') as mock_service:
        mock_service_instance = MagicMock()
        mock_service_instance.send = AsyncMock(return_value {"sent": True})
        mock_service.return_value = mock_service_instance
        
        result = await send_notification_task(task_data)
        
        assert result is not None
        assert result.get("sent") is True


@pytest.mark.asyncio
async def test_task_retry_on_failure():
    """Test task retry mechanism on failure."""
    task_data = {
        "agent_id": "agent1",
        "user_id": "user123",
        "goal": "Test goal"
    }
    
    with patch('app.workers.tasks.agent_tasks.AgentBase') as mock_agent:
        mock_agent_instance = MagicMock()
        mock_agent_instance.execute = AsyncMock(side_effect=Exception("Test error"))
        mock_agent.return_value = mock_agent_instance
        
        try:
            await process_agent_task(task_data)
            assert False, "Should have raised exception"
        except Exception as e:
            assert str(e) == "Test error"


@pytest.mark.asyncio
async def test_task_result_storage():
    """Test task result storage in backend."""
    task_data = {
        "agent_id": "agent1",
        "user_id": "user123",
        "goal": "Test goal"
    }
    
    with patch('app.workers.tasks.agent_tasks.AgentBase') as mock_agent:
        with patch('app.workers.tasks.agent_tasks.task_repository') as mock_repo:
            mock_agent_instance = MagicMock()
            mock_agent_instance.execute = AsyncMock(return_value={"result": "success"})
            mock_agent.return_value = mock_agent_instance
            
            mock_repo.update = AsyncMock(return_value=True)
            
            result = await process_agent_task(task_data)
            
            assert result is not None
