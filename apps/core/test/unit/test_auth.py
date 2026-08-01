"""Unit tests for auth module."""

from unittest.mock import AsyncMock, patch

import pytest
from app.auth.models import UserCreate, UserLogin
from app.auth.service import AuthService


@pytest.fixture
def auth_service():
    """Create auth service fixture."""
    with patch('app.auth.service.user_repository') as mock_repo:
        return AuthService(mock_repo)


@pytest.fixture
def user_create():
    """Create user create fixture."""
    return UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        name="Test User"
    )


@pytest.fixture
def user_login():
    """Create user login fixture."""
    return UserLogin(
        email="test@example.com",
        password="TestPassword123!"
    )


# Auth Service Tests
@pytest.mark.asyncio
async def test_auth_service_register_user(auth_service, user_create):
    """Test user registration."""
    with patch.object(auth_service.user_repo, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = {"id": "user123", "email": user_create.email}

        result = await auth_service.register_user(user_create)

        assert result["email"] == user_create.email
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_auth_service_login_user(auth_service, user_login):
    """Test user login."""
    with patch.object(auth_service, '_verify_password', return_value=True):
        with patch.object(auth_service, '_create_tokens', return_value={"access": "token", "refresh": "refresh_token"}):
            with patch.object(auth_service.user_repo, 'get_by_email', new_callable=AsyncMock) as mock_get:
                mock_get.return_value = {"id": "user123", "email": user_login.email}

                result = await auth_service.login_user(user_login)

                assert "access" in result
                assert "refresh" in result


@pytest.mark.asyncio
async def test_auth_service_login_invalid_password(auth_service, user_login):
    """Test login with invalid password."""
    with patch.object(auth_service, '_verify_password', return_value=False):
        with patch.object(auth_service.user_repo, 'get_by_email', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"id": "user123", "email": user_login.email}

            with pytest.raises(ValueError):
                await auth_service.login_user(user_login)


@pytest.mark.asyncio
async def test_auth_service_refresh_token(auth_service):
    """Test token refresh."""
    with patch.object(auth_service, '_decode_refresh_token', return_value={"sub": "user123"}):
        with patch.object(auth_service, '_create_tokens', return_value={"access": "new_token", "refresh": "new_refresh"}):
            result = await auth_service.refresh_token("valid_refresh_token")

            assert "access" in result
            assert "refresh" in result


@pytest.mark.asyncio
async def test_auth_service_logout(auth_service):
    """Test user logout."""
    with patch.object(auth_service, '_invalidate_token', return_value=True):
        result = await auth_service.logout("access_token")

        assert result is True


@pytest.mark.asyncio
async def test_auth_service_verify_token(auth_service):
    """Test token verification."""
    with patch.object(auth_service, '_decode_access_token', return_value={"sub": "user123"}):
        result = await auth_service.verify_token("valid_token")

        assert result["sub"] == "user123"


# User Model Tests
def test_user_create_validation(user_create):
    """Test user create validation."""
    assert user_create.email == "test@example.com"
    assert user_create.password == "TestPassword123!"
    assert user_create.name == "Test User"


def test_user_login_validation(user_login):
    """Test user login validation."""
    assert user_login.email == "test@example.com"
    assert user_login.password == "TestPassword123!"


def test_user_create_invalid_email():
    """Test user create with invalid email."""
    with pytest.raises(ValueError):
        UserCreate(email="invalid", password="Test123!", name="Test")


def test_user_create_weak_password():
    """Test user create with weak password."""
    with pytest.raises(ValueError):
        UserCreate(email="test@example.com", password="weak", name="Test")
