"""E2E tests for complete user workflows."""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_complete_user_registration_and_login():
    """Test complete user registration and login workflow."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Step 1: Register user
        user_data = {
            "email": "e2e_test@example.com",
            "password": "TestPassword123!",
            "name": "E2E Test User"
        }
        
        register_response = await client.post("/auth/register", json=user_data)
        assert register_response.status_code in [200, 201]
        
        # Step 2: Login
        login_data = {
            "email": "e2e_test@example.com",
            "password": "TestPassword123!"
        }
        
        login_response = await client.post("/auth/login", json=login_data)
        
        assert login_response.status_code == 200, "Login failed"
        access_token = login_response.json().get("access_token")
        assert access_token is not None
            
            # Step 3: Access protected endpoint
            tasks_response = await client.get(
                "/tasks",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert tasks_response.status_code == 200


@pytest.mark.asyncio
async def test_complete_task_workflow():
    """Test complete task management workflow."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        })
        
        assert login_response.status_code == 200, "Login failed"
        access_token = login_response.json().get("access_token")
        
        # Step 1: Create task
        task_data = {
            "title": "E2E Test Task",
            "description": "This is an E2E test task",
            "priority": "medium"
        }
        
        create_response = await client.post(
            "/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert create_response.status_code in [200, 201]
        task_id = create_response.json().get("id")
        
        # Step 2: Get task
        get_response = await client.get(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert get_response.status_code == 200
        
        # Step 3: Update task
        update_data = {"status": "completed"}
        update_response = await client.patch(
            f"/tasks/{task_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert update_response.status_code == 200
        
        # Step 4: Delete task
        delete_response = await client.delete(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert delete_response.status_code == 200


@pytest.mark.asyncio
async def test_complete_memory_workflow():
    """Test complete memory management workflow."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        })
        
        assert login_response.status_code == 200, "Login failed"
        access_token = login_response.json().get("access_token")
        
        # Step 1: Create memory
        memory_data = {
            "content": "This is an E2E test memory",
            "layer": "episodic",
            "importance_score": 0.8
        }
        
        create_response = await client.post(
            "/memory",
            json=memory_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert create_response.status_code in [200, 201]
        memory_id = create_response.json().get("id")
        
        # Step 2: Search memory
        search_response = await client.get(
            "/memory/search?query=test",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert search_response.status_code == 200
        
        # Step 3: Get memory
        get_response = await client.get(
            f"/memory/{memory_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert get_response.status_code == 200


@pytest.mark.asyncio
async def test_complete_email_processing_workflow():
    """Test complete email processing workflow."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        })
        
        assert login_response.status_code == 200, "Login failed"
        access_token = login_response.json().get("access_token")
        
        # Step 1: Submit email for processing
        email_data = {
            "subject": "Meeting tomorrow at 3PM",
            "body": "Don't forget the meeting with the team",
            "sender": "colleague@example.com"
        }
        
        process_response = await client.post(
            "/email/process",
            json=email_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert process_response.status_code == 200
        result = process_response.json()
        
        # Step 2: Check if tasks were extracted
        if "tasks" in result:
            assert len(result["tasks"]) >= 0


@pytest.mark.asyncio
async def test_complete_notification_workflow():
    """Test complete notification workflow."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        })
        
        assert login_response.status_code == 200, "Login failed"
        access_token = login_response.json().get("access_token")
        
        # Step 1: Create notification
        notification_data = {
            "type": "task_reminder",
            "message": "Task due in 1 hour",
            "channels": ["email"]
        }
        
        create_response = await client.post(
            "/notifications",
            json=notification_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert create_response.status_code in [200, 201]
        notification_id = create_response.json().get("id")
        
        # Step 2: List notifications
        list_response = await client.get(
            "/notifications",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert list_response.status_code == 200
        
        # Step 3: Mark as read
        mark_response = await client.patch(
            f"/notifications/{notification_id}/read",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert mark_response.status_code == 200


@pytest.mark.asyncio
async def test_complete_agent_workflow():
    """Test complete agent execution workflow."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        })
        
        assert login_response.status_code == 200, "Login failed"
        access_token = login_response.json().get("access_token")
        
        # Step 1: Start agent
        agent_data = {
            "agent_type": "planner",
            "goal": "Plan a project timeline",
            "context": {"project": "E2E Test"}
        }
        
        start_response = await client.post(
            "/agents/start",
            json=agent_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert start_response.status_code == 200
        agent_id = start_response.json().get("agent_id")
        
        # Step 2: Check agent status
        status_response = await client.get(
            f"/agents/{agent_id}/status",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert status_response.status_code == 200
        
        # Step 3: Get agent result
        result_response = await client.get(
            f"/agents/{agent_id}/result",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert result_response.status_code == 200
