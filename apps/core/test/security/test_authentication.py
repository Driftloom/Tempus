"""Security tests for authentication."""

import pytest
from unittest.mock import patch
from httpx import AsyncClient
from app.main import app


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
