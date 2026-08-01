"""Encryption utilities for sensitive data."""

from cryptography.fernet import Fernet
from structlog import get_logger

from app.core.config import settings

logger = get_logger(__name__)


class EncryptionManager:
    """Manager for encryption/decryption operations."""

    def __init__(self):
        """Initialize encryption manager."""
        self.key = settings.encryption_key.encode()
        self.cipher = Fernet(self.key)

    def encrypt(self, data: str) -> str:
        """Encrypt string data."""
        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt encrypted string data."""
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()
