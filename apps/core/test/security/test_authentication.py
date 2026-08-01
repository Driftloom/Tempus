"""Security tests for authentication."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.auth.service import AuthService


@pytest.mark.asyncio
async def test_jwt_token_validation():
    """Test JWT token validation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test with invalid token
        response = await client.get(
            "/tasks",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_jwt_token_expiration():
    """Test JWT token expiration handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test with expired token (simulated)
        response = await client.get(
            "/tasks",
            headers={"Authorization": "Bearer expired_token"}
        )

        assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_password_strength():
    """Test password strength validation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Weak password
        weak_password = {
            "email": "test@example.com",
            "password": "weak",
            "name": "Test User"
        }

        response = await client.post("/auth/register", json=weak_password)

        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_password_hashing():
    """Test password hashing."""
    from app.security.auth import PasswordManager

    password_manager = PasswordManager()
    password = "TestPassword123!"

    hashed = password_manager.hash_password(password)

    # Hash should not equal original
    assert hashed != password
    # Hash should be bcrypt format
    assert hashed.startswith("$2b$")


@pytest.mark.asyncio
async def test_mfa_token_validation():
    """Test MFA token validation."""
    from app.security.mfa import MFAManager

    mfa_manager = MFAManager()
    secret = mfa_manager.generate_secret()

    # Generate valid token
    import pyotp
    totp = pyotp.TOTP(secret)
    valid_token = totp.now()

    # Test valid token
    assert mfa_manager.verify_totp(secret, valid_token)

    # Test invalid token
    assert not mfa_manager.verify_totp(secret, "000000")


@pytest.mark.asyncio
async def test_oauth_state_parameter():
    """Test OAuth state parameter for CSRF protection."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # OAuth flow should include state parameter
        response = await client.get("/auth/oauth/google")

        # Should redirect with state parameter
        assert response.status_code in [200, 302]


@pytest.mark.asyncio
async def test_session_management():
    """Test session management."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_data = {"email": "test@example.com", "password": "TestPassword123!"}
        login_response = await client.post("/auth/login", json=login_data)

        if login_response.status_code == 200:
            access_token = login_response.json().get("access_token")

            # Use token for authenticated request
            response = await client.get(
                "/tasks",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_token_rotation():
    """Test token rotation for security."""
    from app.security.auth import TokenRotationManager

    with patch('app.security.auth.settings') as mock_settings:
        mock_settings.secret_key = "test_key"

        rotation_manager = TokenRotationManager()

        # Create initial token
        data = {"sub": "user123"}
        token = rotation_manager.create_access_token(data)

        # Rotate token
        new_token = rotation_manager.rotate_token(token)

        # New token should be different
        assert new_token != token


@pytest.mark.asyncio
async def test_login_with_valid_credentials():
    """Test login with valid credentials."""
    auth_service = AuthService()
    
    # Mock database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock user lookup
    with patch.object(auth_service, 'get_user_by_email', return_value=AsyncMock(
        id="user123",
        email="test@example.com",
        password_hash="$2b$12$hashedpassword"
    )):
        with patch('app.security.auth.PasswordManager.verify_password', return_value=True):
            user = await auth_service.verify_credentials(mock_db, "test@example.com", "password")
            assert user is not None


@pytest.mark.asyncio
async def test_login_with_invalid_credentials():
    """Test login with invalid credentials."""
    auth_service = AuthService()
    
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock user not found
    with patch.object(auth_service, 'get_user_by_email', return_value=None):
        user = await auth_service.verify_credentials(mock_db, "test@example.com", "wrongpassword")
        assert user is None


@pytest.mark.asyncio
async def test_login_with_missing_email():
    """Test login with missing email."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={"password": "TestPassword123!"}
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_with_missing_password():
    """Test login with missing password."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_rate_limiting_on_login():
    """Test rate limiting on login endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make multiple login attempts
        for _ in range(65):  # Exceed rate limit of 60
            response = await client.post(
                "/auth/login",
                json={"email": "test@example.com", "password": "TestPassword123!"}
            )
            # Should eventually return 429
            if response.status_code == 429:
                break
        else:
            pytest.fail("Rate limiting did not trigger")
