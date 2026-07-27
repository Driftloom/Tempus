"""Integration tests for database operations."""

import pytest
from sqlalchemy import select
from app.database.models.user import User
from app.database.models.task import Task, TaskStatus, TaskPriority
from app.database.models.memory import MemoryItem, MemoryLayer


@pytest.mark.asyncio
async def test_create_user(test_db):
    """Test creating a user."""
    user = User(
        id="test-user-1",
        email="test@example.com",
        name="Test User",
    )
    
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    assert user.id == "test-user-1"
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_create_task(test_db):
    """Test creating a task."""
    user = User(id="test-user-2", email="test2@example.com", name="Test User 2")
    test_db.add(user)
    await test_db.commit()
    
    task = Task(
        id="test-task-1",
        user_id=user.id,
        title="Test Task",
        description="Test description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
    )
    
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)
    
    assert task.id == "test-task-1"
    assert task.user_id == user.id
    assert task.status == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_create_memory(test_db):
    """Test creating a memory."""
    user = User(id="test-user-3", email="test3@example.com", name="Test User 3")
    test_db.add(user)
    await test_db.commit()
    
    memory = MemoryItem(
        id="test-memory-1",
        user_id=user.id,
        content="Test memory content",
        layer=MemoryLayer.EPISODIC,
        importance_score=0.8,
    )
    
    test_db.add(memory)
    await test_db.commit()
    await test_db.refresh(memory)
    
    assert memory.id == "test-memory-1"
    assert memory.user_id == user.id
    assert memory.layer == MemoryLayer.EPISODIC


@pytest.mark.asyncio
async def test_user_task_relationship(test_db):
    """Test user-task relationship."""
    user = User(id="test-user-4", email="test4@example.com", name="Test User 4")
    test_db.add(user)
    await test_db.commit()
    
    task = Task(
        id="test-task-2",
        user_id=user.id,
        title="Test Task 2",
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH,
    )
    test_db.add(task)
    await test_db.commit()
    
    # Query tasks for user
    result = await test_db.execute(
        select(Task).where(Task.user_id == user.id)
    )
    tasks = result.scalars().all()
    
    assert len(tasks) == 1
    assert tasks[0].id == "test-task-2"


@pytest.mark.asyncio
async def test_update_task_status(test_db):
    """Test updating task status."""
    user = User(id="test-user-5", email="test5@example.com", name="Test User 5")
    test_db.add(user)
    await test_db.commit()
    
    task = Task(
        id="test-task-3",
        user_id=user.id,
        title="Test Task 3",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
    )
    test_db.add(task)
    await test_db.commit()
    
    # Update status
    task.status = TaskStatus.COMPLETED
    await test_db.commit()
    await test_db.refresh(task)
    
    assert task.status == TaskStatus.COMPLETED
