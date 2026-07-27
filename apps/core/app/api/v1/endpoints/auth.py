"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth.jwt_handler import JWTHandler
from app.auth.dependencies import get_current_user

router = APIRouter()
jwt_handler = JWTHandler()


class LoginRequest(BaseModel):
    """Login request schema."""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
    user_id: str


@router.post("/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """Authenticate user and return JWT token."""
    # In production, would validate credentials against database
    # For now, accept any credentials for development
    
    user_id = "default-user"  # Would come from database lookup
    
    # Create access token
    access_token = jwt_handler.create_access_token(
        data={"sub": user_id, "email": login_data.email}
    )
    
    return TokenResponse(access_token=access_token, user_id=user_id)


@router.get("/auth/me")
async def get_me(current_user: str = Depends(get_current_user)):
    """Get current user information."""
    return {
        "user_id": current_user,
        "email": "user@example.com"  # Would come from database
    }
