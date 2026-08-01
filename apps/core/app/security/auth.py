"""JWT and OAuth2 authentication."""

from datetime import datetime, timedelta
from typing import Any

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token security
security = HTTPBearer()


class TokenManager:
    """Manager for JWT token operations."""

    def __init__(self):
        """Initialize token manager."""
        self.secret_key = settings.jwt_secret
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

    def create_access_token(self, data: dict[str, Any]) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: dict[str, Any]) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and validate JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.error("Token decode failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    def verify_token_type(self, payload: dict[str, Any], token_type: str) -> bool:
        """Verify token type."""
        return payload.get("type") == token_type


class PasswordManager:
    """Manager for password operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)


class APIKeyManager:
    """Manager for API key operations."""

    def __init__(self):
        """Initialize API key manager."""
        self.secret_key = settings.jwt_secret

    def generate_api_key(self, user_id: str, name: str) -> str:
        """Generate API key for user."""
        import secrets
        key_prefix = f"tempus_{user_id[:8]}"
        key_suffix = secrets.token_urlsafe(32)
        return f"{key_prefix}_{key_suffix}"

    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key format."""
        if not api_key.startswith("tempus_"):
            return False
        parts = api_key.split("_")
        return len(parts) >= 3


class TokenRotationManager:
    """Manager for token rotation."""

    def __init__(self, token_manager: TokenManager):
        """Initialize token rotation manager."""
        self.token_manager = token_manager
        self.rotation_threshold_minutes = 15

    def should_rotate_token(self, payload: dict[str, Any]) -> bool:
        """Check if token should be rotated."""
        exp = payload.get("exp")
        if not exp:
            return True

        exp_datetime = datetime.fromtimestamp(exp)
        time_until_expiry = exp_datetime - datetime.utcnow()

        return time_until_expiry.total_seconds() < (self.rotation_threshold_minutes * 60)

    def rotate_token(self, payload: dict[str, Any]) -> str:
        """Rotate token."""
        # Remove exp and type from payload
        data = {k: v for k, v in payload.items() if k not in ["exp", "type"]}
        return self.token_manager.create_access_token(data)


# Global instances
token_manager = TokenManager()
password_manager = PasswordManager()
api_key_manager = APIKeyManager()
token_rotation_manager = TokenRotationManager(token_manager)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict[str, Any]:
    """Get current user from JWT token."""
    token = credentials.credentials
    payload = token_manager.decode_token(token)

    if not token_manager.verify_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return {"user_id": user_id, "payload": payload}
