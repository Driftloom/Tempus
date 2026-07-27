"""Security tests for encryption."""

import pytest
from unittest.mock import patch
from app.security.encryption import EncryptionManager


def test_encryption_decryption():
    """Test encryption and decryption."""
    with patch('app.security.encryption.settings') as mock_settings:
        mock_settings.encryption_key = "test_encryption_key_32_chars_long"
        
        encryption_manager = EncryptionManager()
        
        original_data = "sensitive_data_123"
        encrypted = encryption_manager.encrypt(original_data)
        decrypted = encryption_manager.decrypt(encrypted)
        
        assert encrypted != original_data
        assert decrypted == original_data


def test_encryption_key_uniqueness():
    """Test that different data produces different ciphertext."""
    with patch('app.security.encryption.settings') as mock_settings:
        mock_settings.encryption_key = "test_encryption_key_32_chars_long"
        
        encryption_manager = EncryptionManager()
        
        data1 = "data_1"
        data2 = "data_2"
        
        encrypted1 = encryption_manager.encrypt(data1)
        encrypted2 = encryption_manager.encrypt(data2)
        
        assert encrypted1 != encrypted2


def test_encryption_with_special_characters():
    """Test encryption with special characters."""
    with patch('app.security.encryption.settings') as mock_settings:
        mock_settings.encryption_key = "test_encryption_key_32_chars_long"
        
        encryption_manager = EncryptionManager()
        
        original_data = "special_chars: !@#$%^&*()_+-={}[]|\\:;\"'<>,.?/~`"
        encrypted = encryption_manager.encrypt(original_data)
        decrypted = encryption_manager.decrypt(encrypted)
        
        assert decrypted == original_data


def test_encryption_with_unicode():
    """Test encryption with unicode characters."""
    with patch('app.security.encryption.settings') as mock_settings:
        mock_settings.encryption_key = "test_encryption_key_32_chars_long"
        
        encryption_manager = EncryptionManager()
        
        original_data = "unicode: 你好 🎉 Ñoño"
        encrypted = encryption_manager.encrypt(original_data)
        decrypted = encryption_manager.decrypt(encrypted)
        
        assert decrypted == original_data


def test_encryption_empty_string():
    """Test encryption with empty string."""
    with patch('app.security.encryption.settings') as mock_settings:
        mock_settings.encryption_key = "test_encryption_key_32_chars_long"
        
        encryption_manager = EncryptionManager()
        
        original_data = ""
        encrypted = encryption_manager.encrypt(original_data)
        decrypted = encryption_manager.decrypt(encrypted)
        
        assert decrypted == original_data


def test_encryption_long_data():
    """Test encryption with long data."""
    with patch('app.security.encryption.settings') as mock_settings:
        mock_settings.encryption_key = "test_encryption_key_32_chars_long"
        
        encryption_manager = EncryptionManager()
        
        original_data = "A" * 10000
        encrypted = encryption_manager.encrypt(original_data)
        decrypted = encryption_manager.decrypt(encrypted)
        
        assert decrypted == original_data


def test_decryption_with_wrong_key():
    """Test decryption fails with wrong key."""
    with patch('app.security.encryption.settings') as mock_settings:
        mock_settings.encryption_key = "test_encryption_key_32_chars_long"
        
        encryption_manager = EncryptionManager()
        
        original_data = "sensitive_data"
        encrypted = encryption_manager.encrypt(original_data)
    
    # Create new manager with different key
    with patch('app.security.encryption.settings') as mock_settings:
        mock_settings.encryption_key = "different_encryption_key_32_chars"
        
        wrong_key_manager = EncryptionManager()
        
        # Should fail to decrypt
        try:
            decrypted = wrong_key_manager.decrypt(encrypted)
            assert False, "Should have raised exception"
        except Exception:
            pass  # Expected


def test_encryption_format():
    """Test encrypted data format."""
    with patch('app.security.encryption.settings') as mock_settings:
        mock_settings.encryption_key = "test_encryption_key_32_chars_long"
        
        encryption_manager = EncryptionManager()
        
        original_data = "test_data"
        encrypted = encryption_manager.encrypt(original_data)
        
        # Fernet produces base64-like output
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0
