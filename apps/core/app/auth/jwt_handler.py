"""JWT handler for authentication."""

from datetime import datetime, timedelta
from typing import Dict
from jose import JWTError, jwt
from app.core.config import settings

class JWTHandler:
    """Handler for JWT token operations."""
    
    def __init__(self):
        """Initialize JWT handler."""
        self.secret_key = settings.jwt_secret
        self.algorithm = settings.jwt_algorithm
        self.expiration_minutes = settings.jwt_expiration_minutes
    
    def create_access_token(self, data: Dict) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.expiration_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_access_token(self, token: str) -> Dict:
        """Decode and validate JWT access token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
