"""Security tests for input validation."""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_sql_injection_prevention():
    """Test SQL injection prevention."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # SQL injection attempt
        malicious_input = {
            "title": "'; DROP TABLE users; --",
            "description": "Test"
        }
        
        response = await client.post(
            "/tasks",
            json=malicious_input,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should either reject or handle safely
        assert response.status_code in [400, 401, 422]


@pytest.mark.asyncio
async def test_xss_prevention():
    """Test XSS prevention."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # XSS attempt
        malicious_input = {
            "title": "<script>alert('XSS')</script>",
            "description": "Test"
        }
        
        response = await client.post(
            "/tasks",
            json=malicious_input,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should either reject or sanitize
        assert response.status_code in [400, 401, 422, 200]
        
        if response.status_code == 200:
            # Check if script tag was escaped
            data = response.json()
            assert "<script>" not in str(data.get("title", ""))


@pytest.mark.asyncio
async def test_command_injection_prevention():
    """Test command injection prevention."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Command injection attempt
        malicious_input = {
            "title": "test; rm -rf /",
            "description": "Test"
        }
        
        response = await client.post(
            "/tasks",
            json=malicious_input,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should either reject or handle safely
        assert response.status_code in [400, 401, 422]


@pytest.mark.asyncio
async def test_path_traversal_prevention():
    """Test path traversal prevention."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Path traversal attempt
        response = await client.get("/files/../../../etc/passwd")
        
        assert response.status_code in [400, 403, 404]


@pytest.mark.asyncio
async def test_large_payload_rejection():
    """Test large payload rejection."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Very large payload
        large_data = {
            "title": "A" * 10000,
            "description": "B" * 100000
        }
        
        response = await client.post(
            "/tasks",
            json=large_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should reject large payloads
        assert response.status_code in [400, 413, 422]


@pytest.mark.asyncio
async def test_malformed_json():
    """Test malformed JSON handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Malformed JSON
        response = await client.post(
            "/tasks",
            data="{invalid json}",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_content_type_validation():
    """Test content-type validation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Wrong content type
        response = await client.post(
            "/tasks",
            data="title=test",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [400, 415, 422]


@pytest.mark.asyncio
async def test_email_validation():
    """Test email format validation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Invalid email
        invalid_data = {
            "email": "not-an-email",
            "password": "TestPassword123!",
            "name": "Test User"
        }
        
        response = await client.post("/auth/register", json=invalid_data)
        
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_special_characters_handling():
    """Test special characters handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Input with special characters
        special_data = {
            "title": "Test with special chars: <>&\"'",
            "description": "Test"
        }
        
        response = await client.post(
            "/tasks",
            json=special_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should handle safely
        assert response.status_code in [200, 400, 401, 422]
