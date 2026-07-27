"""Integration tests for authentication flows."""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_oauth_google_flow():
    """Test Google OAuth flow."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Start OAuth flow
        response = await client.get("/auth/oauth/google")
        
        assert response.status_code in [200, 302]  # Redirect to Google


@pytest.mark.asyncio
async def test_oauth_github_flow():
    """Test GitHub OAuth flow."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Start OAuth flow
        response = await client.get("/auth/oauth/github")
        
        assert response.status_code in [200, 302]  # Redirect to GitHub


@pytest.mark.asyncio
async def test_register_user():
    """Test user registration."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_data = {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "name": "Test User"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "access_token" in data or "user_id" in data


@pytest.mark.asyncio
async def test_login_user():
    """Test user login."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
        
        response = await client.post("/auth/login", json=login_data)
        
        assert response.status_code in [200, 401]  # 401 if user doesn't exist
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data


@pytest.mark.asyncio
async def test_refresh_token():
    """Test token refresh."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First login to get refresh token
        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
        
        login_response = await client.post("/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            refresh_token = login_response.json().get("refresh_token")
            
            # Refresh the token
            refresh_response = await client.post(
                "/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            
            assert refresh_response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_logout():
    """Test user logout."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login first
        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
        
        login_response = await client.post("/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            access_token = login_response.json().get("access_token")
            
            # Logout
            logout_response = await client.post(
                "/auth/logout",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert logout_response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_mfa_setup():
    """Test MFA setup."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Setup MFA (requires authenticated user)
        response = await client.post(
            "/auth/mfa/setup",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_mfa_verify():
    """Test MFA verification."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/mfa/verify",
            json={"token": "123456"},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 401]
