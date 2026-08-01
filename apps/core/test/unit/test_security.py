"""Unit tests for security module."""

from unittest.mock import patch

import pytest

from app.security.auth import (
    APIKeyManager,
    PasswordManager,
    TokenManager,
)
from app.security.encryption import EncryptionManager
from app.security.mfa import MFAManager, RecoveryCodeManager
from app.security.rbac import ABACManager, Permission, RBACManager, Role
from app.security.secret_rotation import SecretManager


@pytest.fixture
def token_manager():
    """Create token manager fixture."""
    with patch('app.security.auth.settings') as mock_settings:
        mock_settings.secret_key = "test_secret_key_for_testing"
        return TokenManager()


@pytest.fixture
def password_manager():
    """Create password manager fixture."""
    return PasswordManager()


@pytest.fixture
def api_key_manager():
    """Create API key manager fixture."""
    with patch('app.security.auth.settings') as mock_settings:
        mock_settings.secret_key = "test_secret_key"
        return APIKeyManager()


@pytest.fixture
def rbac_manager():
    """Create RBAC manager fixture."""
    return RBACManager()


@pytest.fixture
def abac_manager():
    """Create ABAC manager fixture."""
    return ABACManager()


@pytest.fixture
def mfa_manager():
    """Create MFA manager fixture."""
    return MFAManager()


@pytest.fixture
def recovery_code_manager():
    """Create recovery code manager fixture."""
    return RecoveryCodeManager()


@pytest.fixture
def secret_manager():
    """Create secret manager fixture."""
    return SecretManager()


@pytest.fixture
def encryption_manager():
    """Create encryption manager fixture."""
    with patch('app.security.encryption.settings') as mock_settings:
        mock_settings.encryption_key = "test_encryption_key_32_chars_long"
        return EncryptionManager()


# Token Manager Tests
def test_create_access_token(token_manager):
    """Test access token creation."""
    data = {"sub": "user123", "email": "test@example.com"}
    token = token_manager.create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_token(token_manager):
    """Test token decoding."""
    data = {"sub": "user123", "email": "test@example.com"}
    token = token_manager.create_access_token(data)
    payload = token_manager.decode_token(token)

    assert payload["sub"] == "user123"
    assert payload["email"] == "test@example.com"


def test_verify_token_type(token_manager):
    """Test token type verification."""
    data = {"sub": "user123"}
    token = token_manager.create_access_token(data)
    payload = token_manager.decode_token(token)

    assert token_manager.verify_token_type(payload, "access")
    assert not token_manager.verify_token_type(payload, "refresh")


# Password Manager Tests
def test_hash_password(password_manager):
    """Test password hashing."""
    password = "test_password_123"
    hashed = password_manager.hash_password(password)

    assert isinstance(hashed, str)
    assert hashed != password
    assert hashed.startswith("$2b$")


def test_verify_password(password_manager):
    """Test password verification."""
    password = "test_password_123"
    hashed = password_manager.hash_password(password)

    assert password_manager.verify_password(password, hashed)
    assert not password_manager.verify_password("wrong_password", hashed)


# API Key Manager Tests
def test_generate_api_key(api_key_manager):
    """Test API key generation."""
    api_key = api_key_manager.generate_api_key("user123", "Test Key")

    assert isinstance(api_key, str)
    assert api_key.startswith("tempus_user123")
    assert len(api_key) > 20


def test_validate_api_key(api_key_manager):
    """Test API key validation."""
    api_key = api_key_manager.generate_api_key("user123", "Test Key")

    assert api_key_manager.validate_api_key(api_key)
    assert not api_key_manager.validate_api_key("invalid_key")


# RBAC Manager Tests
def test_get_permissions_for_role(rbac_manager):
    """Test getting permissions for role."""
    permissions = rbac_manager.get_permissions_for_role(Role.USER)

    assert isinstance(permissions, set)
    assert Permission.USER_READ in permissions
    assert Permission.ADMIN_READ not in permissions


def test_has_permission(rbac_manager):
    """Test permission check."""
    assert rbac_manager.has_permission(Role.USER, Permission.USER_READ)
    assert not rbac_manager.has_permission(Role.USER, Permission.ADMIN_READ)


def test_has_any_permission(rbac_manager):
    """Test any permission check."""
    assert rbac_manager.has_any_permission(Role.USER, [Permission.USER_READ, Permission.ADMIN_READ])
    assert not rbac_manager.has_any_permission(Role.USER, [Permission.ADMIN_READ, Permission.ADMIN_WRITE])


def test_has_all_permissions(rbac_manager):
    """Test all permissions check."""
    assert rbac_manager.has_all_permissions(Role.USER, [Permission.USER_READ, Permission.USER_WRITE])
    assert not rbac_manager.has_all_permissions(Role.USER, [Permission.USER_READ, Permission.ADMIN_READ])


# ABAC Manager Tests
def test_check_access_owner(abac_manager):
    """Test access check for resource owner."""
    assert abac_manager.check_access(
        Role.USER,
        Permission.TASK_READ,
        "user123",
        resource_id="task1",
        resource_owner_id="user123"
    )


def test_check_access_admin(abac_manager):
    """Test access check for admin."""
    assert abac_manager.check_access(
        Role.ADMIN,
        Permission.TASK_READ,
        "admin123",
        resource_id="task1",
        resource_owner_id="user123"
    )


def test_check_access_denied(abac_manager):
    """Test access denied."""
    assert not abac_manager.check_access(
        Role.USER,
        Permission.ADMIN_READ,
        "user123",
        resource_id="task1",
        resource_owner_id="user456"
    )


# MFA Manager Tests
def test_mfa_generate_secret(mfa_manager):
    """Test MFA secret generation."""
    secret = mfa_manager.generate_secret()

    assert isinstance(secret, str)
    assert len(secret) == 32


def test_generate_totp_uri(mfa_manager):
    """Test TOTP URI generation."""
    secret = mfa_manager.generate_secret()
    uri = mfa_manager.generate_totp_uri(secret, "test@example.com")

    assert isinstance(uri, str)
    assert "otpauth://totp" in uri
    assert "test@example.com" in uri


def test_verify_totp(mfa_manager):
    """Test TOTP verification."""
    secret = mfa_manager.generate_secret()
    # Generate a valid token (this would normally come from authenticator app)
    import pyotp
    totp = pyotp.TOTP(secret)
    token = totp.now()

    assert mfa_manager.verify_totp(secret, token)


# Recovery Code Manager Tests
def test_generate_recovery_codes(recovery_code_manager):
    """Test recovery code generation."""
    codes = recovery_code_manager.generate_recovery_codes()

    assert isinstance(codes, list)
    assert len(codes) == 10
    assert all(len(code) == 10 for code in codes)


def test_verify_recovery_code(recovery_code_manager):
    """Test recovery code verification."""
    codes = recovery_code_manager.generate_recovery_codes()

    assert recovery_code_manager.verify_recovery_code(codes[0], codes)
    assert not recovery_code_manager.verify_recovery_code("invalid", codes)


# Secret Manager Tests
def test_generate_secret(secret_manager):
    """Test secret generation."""
    secret = secret_manager.generate_secret()

    assert isinstance(secret, str)
    assert len(secret) > 30


def test_store_and_get_secret(secret_manager):
    """Test secret storage and retrieval."""
    secret = secret_manager.generate_secret()
    secret_manager.store_secret("test_key", secret)

    retrieved = secret_manager.get_secret("test_key")
    assert retrieved == secret


def test_rotate_secret(secret_manager):
    """Test secret rotation."""
    secret = secret_manager.generate_secret()
    secret_manager.store_secret("test_key", secret)

    new_secret = secret_manager.rotate_secret("test_key")

    assert new_secret != secret
    assert secret_manager.get_secret("test_key") == new_secret


def test_check_rotation_needed(secret_manager):
    """Test rotation check."""
    secret_manager.store_secret("test_key", "secret", rotation_days=0)

    assert secret_manager.check_rotation_needed("test_key")


# Encryption Manager Tests
def test_encrypt_decrypt(encryption_manager):
    """Test encryption and decryption."""
    data = "sensitive_data_123"
    encrypted = encryption_manager.encrypt(data)
    decrypted = encryption_manager.decrypt(encrypted)

    assert encrypted != data
    assert decrypted == data
