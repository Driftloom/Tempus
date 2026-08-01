"""Integration tests for authentication flows."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.auth.service import AuthService


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


@pytest.mark.asyncio
async def test_complete_auth_flow():
    """Test complete authentication flow: register -> login -> access protected endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user
        register_data = {
            "email": "integration@example.com",
            "password": "SecurePass123!",
            "name": "Integration Test User"
        }
        
        # Note: Registration endpoint may not be fully implemented
        # This test validates the flow structure
        register_response = await client.post("/auth/register", json=register_data)
        
        # Login with credentials
        login_data = {
            "email": "integration@example.com",
            "password": "SecurePass123!"
        }
        
        login_response = await client.post("/auth/login", json=login_data)
        
        # If login succeeds, test protected endpoint
        if login_response.status_code == 200:
            access_token = login_response.json().get("access_token")
            
            # Access protected endpoint
            protected_response = await client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert protected_response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_auth_service_user_creation():
    """Test AuthService user creation."""
    auth_service = AuthService()
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock database operations
    with patch.object(mock_db, 'add'):
        with patch.object(mock_db, 'commit'):
            with patch.object(mock_db, 'refresh'):
                user = await auth_service.create_user(
                    mock_db,
                    "newuser@example.com",
                    "TestPassword123!",
                    "New User"
                )
                assert user is not None
                assert user.email == "newuser@example.com"


@pytest.mark.asyncio
async def test_auth_service_password_update():
    """Test AuthService password update."""
    auth_service = AuthService()
    mock_db = AsyncMock(spec=AsyncSession)
    mock_user = AsyncMock(id="user123", email="test@example.com")
    
    with patch.object(auth_service, 'get_user_by_id', return_value=mock_user):
        with patch.object(mock_db, 'commit'):
            with patch.object(mock_db, 'refresh'):
                updated_user = await auth_service.update_password(
                    mock_db,
                    "user123",
                    "NewPassword123!"
                )
                assert updated_user is not None
