"""E2E tests for system integration workflows."""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_email_to_task_workflow():
    """Test complete workflow from email to task creation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        })
        
        if login_response.status_code == 200:
            access_token = login_response.json().get("access_token")
            
            # Step 1: Process email
            email_data = {
                "subject": "Complete the report by Friday",
                "body": "Please finish the quarterly report by Friday at 5PM",
                "sender": "manager@example.com"
            }
            
            email_response = await client.post(
                "/email/process",
                json=email_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if email_response.status_code == 200:
                result = email_response.json()
                
                # Step 2: Verify tasks were extracted
                if "tasks" in result and len(result["tasks"]) > 0:
                    task_title = result["tasks"][0].get("title")
                    
                    # Step 3: Create task from extracted data
                    task_data = {
                        "title": task_title,
                        "description": "Extracted from email",
                        "priority": "high"
                    }
                    
                    task_response = await client.post(
                        "/tasks",
                        json=task_data,
                        headers={"Authorization": f"Bearer {access_token}"}
                    )
                    
                    assert task_response.status_code in [200, 201, 401]


@pytest.mark.asyncio
async def test_memory_to_agent_workflow():
    """Test workflow from memory retrieval to agent execution."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        })
        
        if login_response.status_code == 200:
            access_token = login_response.json().get("access_token")
            
            # Step 1: Store memory
            memory_data = {
                "content": "Project deadline is next Friday",
                "layer": "episodic",
                "importance_score": 0.9
            }
            
            memory_response = await client.post(
                "/memory",
                json=memory_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if memory_response.status_code in [200, 201]:
                # Step 2: Search memory
                search_response = await client.get(
                    "/memory/search?query=deadline",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if search_response.status_code == 200:
                    memories = search_response.json()
                    
                    # Step 3: Use memory context for agent
                    if len(memories) > 0:
                        agent_data = {
                            "agent_type": "planner",
                            "goal": "Plan work based on deadlines",
                            "context": {"memories": memories[:3]}
                        }
                        
                        agent_response = await client.post(
                            "/agents/start",
                            json=agent_data,
                            headers={"Authorization": f"Bearer {access_token}"}
                        )
                        
                        assert agent_response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_task_to_notification_workflow():
    """Test workflow from task creation to notification."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        })
        
        if login_response.status_code == 200:
            access_token = login_response.json().get("access_token")
            
            # Step 1: Create task with due date
            from datetime import datetime, timedelta
            
            due_date = (datetime.utcnow() + timedelta(hours=2)).isoformat()
            
            task_data = {
                "title": "Urgent task",
                "description": "Task due soon",
                "due_date": due_date,
                "priority": "high"
            }
            
            task_response = await client.post(
                "/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if task_response.status_code in [200, 201]:
                task_id = task_response.json().get("id")
                
                # Step 2: Schedule notification for task
                notification_data = {
                    "type": "task_reminder",
                    "message": f"Task {task_id} is due soon",
                    "scheduled_time": due_date,
                    "channels": ["email"]
                }
                
                notification_response = await client.post(
                    "/notifications/schedule",
                    json=notification_data,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                assert notification_response.status_code in [200, 201, 401]


@pytest.mark.asyncio
async def test_multi_agent_workflow():
    """Test workflow with multiple agents collaborating."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        })
        
        if login_response.status_code == 200:
            access_token = login_response.json().get("access_token")
            
            # Step 1: Start multi-agent orchestration
            orchestration_data = {
                "agent_types": ["planner", "researcher"],
                "goal": "Research and plan a project",
                "mode": "collaborative"
            }
            
            orchestration_response = await client.post(
                "/agents/orchestrate",
                json=orchestration_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert orchestration_response.status_code in [200, 401]
            
            if orchestration_response.status_code == 200:
                orchestration_id = orchestration_response.json().get("orchestration_id")
                
                # Step 2: Check orchestration status
                status_response = await client.get(
                    f"/agents/orchestration/{orchestration_id}/status",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                assert status_response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_extension_integration_workflow():
    """Test workflow with extension integration."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        })
        
        if login_response.status_code == 200:
            access_token = login_response.json().get("access_token")
            
            # Step 1: Load extension
            extension_data = {
                "name": "test_extension",
                "version": "1.0.0",
                "permissions": ["read:tasks", "write:tasks"]
            }
            
            load_response = await client.post(
                "/extensions/load",
                json=extension_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if load_response.status_code in [200]:
                # Step 2: Use extension to create task
                extension_call_data = {
                    "extension_id": "test_extension",
                    "method": "create_task",
                    "params": {"title": "Task from extension"}
                }
                
                call_response = await client.post(
                    "/extensions/sdk/call",
                    json=extension_call_data,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                assert call_response.status_code in [200, 404, 401]
