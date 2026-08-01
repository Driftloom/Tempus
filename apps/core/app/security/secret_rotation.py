"""Secret rotation and management."""

import secrets
from datetime import datetime, timedelta

import structlog

logger = structlog.get_logger(__name__)


class SecretManager:
    """Manager for secret operations."""

    def __init__(self) -> None:
        """Initialize secret manager."""
        self.secrets: dict[str, dict] = {}

    def generate_secret(self, length: int = 32) -> str:
        """Generate cryptographically secure random secret."""
        return secrets.token_urlsafe(length)

    def generate_api_secret(self) -> str:
        """Generate API secret."""
        return f"sk_{self.generate_secret(43)}"

    def store_secret(
        self,
        key: str,
        secret: str,
        rotation_days: int = 90
    ) -> None:
        """Store secret with rotation schedule."""
        self.secrets[key] = {
            "secret": secret,
            "created_at": datetime.utcnow(),
            "rotation_days": rotation_days,
            "next_rotation": datetime.utcnow() + timedelta(days=rotation_days),
        }
        logger.info("Secret stored", key=key, rotation_days=rotation_days)

    def get_secret(self, key: str) -> str | None:
        """Get secret by key."""
        secret_data = self.secrets.get(key)
        if secret_data:
            return secret_data["secret"]
        return None

    def rotate_secret(self, key: str) -> str:
        """Rotate secret."""
        if key not in self.secrets:
            raise ValueError(f"Secret {key} not found")

        old_secret_data = self.secrets[key]
        new_secret = self.generate_api_secret()

        self.secrets[key] = {
            "secret": new_secret,
            "created_at": datetime.utcnow(),
            "rotation_days": old_secret_data["rotation_days"],
            "next_rotation": datetime.utcnow() + timedelta(days=old_secret_data["rotation_days"]),
        }

        logger.info("Secret rotated", key=key)
        return new_secret

    def check_rotation_needed(self, key: str) -> bool:
        """Check if secret needs rotation."""
        secret_data = self.secrets.get(key)
        if not secret_data:
            return False

        return datetime.utcnow() >= secret_data["next_rotation"]

    def get_rotation_status(self, key: str) -> dict:
        """Get rotation status for secret."""
        secret_data = self.secrets.get(key)
        if not secret_data:
            return {"exists": False}

        days_until_rotation = (secret_data["next_rotation"] - datetime.utcnow()).days

        return {
            "exists": True,
            "created_at": secret_data["created_at"].isoformat(),
            "next_rotation": secret_data["next_rotation"].isoformat(),
            "days_until_rotation": days_until_rotation,
            "needs_rotation": days_until_rotation <= 0,
        }


class KeyRotationScheduler:
    """Scheduler for automatic key rotation."""

    def __init__(self, secret_manager: SecretManager):
        """Initialize rotation scheduler."""
        self.secret_manager = secret_manager

    async def check_and_rotate_all(self) -> dict[str, bool]:
        """Check and rotate all secrets that need rotation."""
        results = {}

        for key in self.secret_manager.secrets.keys():
            if self.secret_manager.check_rotation_needed(key):
                try:
                    self.secret_manager.rotate_secret(key)
                    results[key] = True
                except Exception as e:
                    logger.error("Secret rotation failed", key=key, error=str(e))
                    results[key] = False
            else:
                results[key] = False

        return results

    async def rotate_specific(self, key: str) -> bool:
        """Rotate specific secret."""
        try:
            self.secret_manager.rotate_secret(key)
            return True
        except Exception as e:
            logger.error("Secret rotation failed", key=key, error=str(e))
            return False


# Global instances
secret_manager = SecretManager()
key_rotation_scheduler = KeyRotationScheduler(secret_manager)
