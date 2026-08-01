"""Integration tests for API CRUD operations."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_task_crud(async_client: AsyncClient, db: AsyncSession):
    """Test task creation via API."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.post(
        "/api/v1/tasks",
        json={"input": "Complete project documentation", "source": "manual"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Complete project documentation"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_get_task_by_id(async_client: AsyncClient, db: AsyncSession):
    """Test getting a specific task by ID."""
    # Login
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create task
    response = await async_client.post(
        "/api/v1/tasks",
        json={"input": "Test task", "source": "manual"},
        headers=headers
    )
    task_id = response.json()["id"]
    
    # Get task by ID
    response = await async_client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test task"


@pytest.mark.asyncio
async def test_update_task_crud(async_client: AsyncClient, db: AsyncSession):
    """Test task update via API."""
    # Login
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create task
    response = await async_client.post(
        "/api/v1/tasks",
        json={"input": "Original task", "source": "manual"},
        headers=headers
    )
    task_id = response.json()["id"]
    
    # Update task
    response = await async_client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated task title", "priority": "high"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated task title"
    assert data["priority"] == "high"


@pytest.mark.asyncio
async def test_complete_task_crud(async_client: AsyncClient, db: AsyncSession):
    """Test marking task as complete via API."""
    # Login
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create task
    response = await async_client.post(
        "/api/v1/tasks",
        json={"input": "Task to complete", "source": "manual"},
        headers=headers
    )
    task_id = response.json()["id"]
    
    # Complete task
    response = await async_client.post(f"/api/v1/tasks/{task_id}/complete", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_list_tasks_with_filters(async_client: AsyncClient, db: AsyncSession):
    """Test listing tasks with status and priority filters."""
    # Login
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create multiple tasks
    await async_client.post(
        "/api/v1/tasks",
        json={"input": "High priority task", "source": "manual"},
        headers=headers
    )
    await async_client.post(
        "/api/v1/tasks",
        json={"input": "Low priority task", "source": "manual"},
        headers=headers
    )
    
    # List all tasks
    response = await async_client.get("/api/v1/tasks", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) >= 2
    
    # Filter by priority
    response = await async_client.get("/api/v1/tasks?priority=high", headers=headers)
    assert response.status_code == 200
    high_priority_tasks = response.json()
    assert all(task["priority"] == "high" for task in high_priority_tasks)


@pytest.mark.asyncio
async def test_task_ownership_enforcement(async_client: AsyncClient, db: AsyncSession):
    """Test that users cannot access other users' tasks."""
    # Login as user1
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "user1@example.com", "password": "password1"}
    )
    token1 = response.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    # Create task as user1
    response = await async_client.post(
        "/api/v1/tasks",
        json={"input": "User1's task", "source": "manual"},
        headers=headers1
    )
    task_id = response.json()["id"]
    
    # Login as user2
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "user2@example.com", "password": "password2"}
    )
    token2 = response.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Try to access user1's task as user2
    response = await async_client.get(f"/api/v1/tasks/{task_id}", headers=headers2)
    assert response.status_code == 403
    
    # Try to update user1's task as user2
    response = await async_client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Hacked title"},
        headers=headers2
    )
    assert response.status_code == 403
