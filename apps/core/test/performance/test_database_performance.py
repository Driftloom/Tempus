"""Performance tests for database operations."""

import pytest
import asyncio
import time
from sqlalchemy import select
from app.database.models.user import User
from app.database.models.task import Task, TaskStatus, TaskPriority


@pytest.mark.asyncio
async def test_database_query_performance(test_db):
    """Test database query performance."""
    # Create test users
    users = []
    for i in range(100):
        user = User(id=f"user_{i}", email=f"user{i}@example.com", name=f"User {i}")
        test_db.add(user)
        users.append(user)
    await test_db.commit()
    
    # Measure query performance
    start_time = time.time()
    
    result = await test_db.execute(select(User).where(User.email.like("%@example.com")))
    users_list = result.scalars().all()
    
    elapsed = time.time() - start_time
    
    print(f"Query time for 100 users: {elapsed * 1000:.2f}ms")
    assert elapsed < 0.5  # Should complete in under 500ms
    assert len(users_list) == 100


@pytest.mark.asyncio
async def test_database_insert_performance(test_db):
    """Test database insert performance."""
    start_time = time.time()
    
    # Batch insert
    tasks = []
    for i in range(50):
        task = Task(
            id=f"task_{i}",
            user_id="user123",
            title=f"Task {i}",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )
        test_db.add(task)
        tasks.append(task)
    
    await test_db.commit()
    
    elapsed = time.time() - start_time
    
    print(f"Insert time for 50 tasks: {elapsed * 1000:.2f}ms")
    assert elapsed < 1.0  # Should complete in under 1 second


@pytest.mark.asyncio
async def test_database_update_performance(test_db):
    """Test database update performance."""
    # Create test task
    task = Task(
        id="task_perf",
        user_id="user123",
        title="Performance test task",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM
    )
    test_db.add(task)
    await test_db.commit()
    
    # Measure update performance
    start_time = time.time()
    
    task.status = TaskStatus.COMPLETED
    await test_db.commit()
    
    elapsed = time.time() - start_time
    
    print(f"Update time: {elapsed * 1000:.2f}ms")
    assert elapsed < 0.1  # Should complete in under 100ms


@pytest.mark.asyncio
async def test_database_concurrent_queries(test_db):
    """Test concurrent database queries."""
    # Create test data
    for i in range(20):
        user = User(id=f"user_concurrent_{i}", email=f"user{i}@example.com", name=f"User {i}")
        test_db.add(user)
    await test_db.commit()
    
    async def query_user(user_id):
        result = await test_db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    start_time = time.time()
    
    # Run concurrent queries
    await asyncio.gather(*[query_user(f"user_concurrent_{i}") for i in range(20)])
    
    elapsed = time.time() - start_time
    
    print(f"Concurrent query time for 20 users: {elapsed * 1000:.2f}ms")
    assert elapsed < 1.0  # Should complete in under 1 second


@pytest.mark.asyncio
async def test_database_index_performance(test_db):
    """Test index performance on indexed vs non-indexed columns."""
    # Create test data
    for i in range(100):
        task = Task(
            id=f"task_index_{i}",
            user_id="user123",
            title=f"Task {i}",
            status=TaskStatus.PENDING if i % 2 == 0 else TaskStatus.COMPLETED,
            priority=TaskPriority.MEDIUM
        )
        test_db.add(task)
    await test_db.commit()
    
    # Query indexed column (user_id)
    start_time = time.time()
    result = await test_db.execute(select(Task).where(Task.user_id == "user123"))
    tasks = result.scalars().all()
    elapsed_indexed = time.time() - start_time
    
    print(f"Indexed query time: {elapsed_indexed * 1000:.2f}ms")
    assert elapsed_indexed < 0.5
