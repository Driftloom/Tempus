"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.jwt_handler import JWTHandler
from app.auth.service import AuthService
from app.database.session import get_db
from app.middleware.rate_limit import rate_limiter

router = APIRouter()
jwt_handler = JWTHandler()
auth_service = AuthService()


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
async def login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    # Apply rate limiting
    identifier = request.client.host
    if not rate_limiter.is_allowed(identifier):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "60"}
        )
    
    # Validate credentials are provided
    if not login_data.email or not login_data.password:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    # Verify credentials against database
    user = await auth_service.verify_credentials(db, login_data.email, login_data.password)
    
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create access token
    access_token = jwt_handler.create_access_token(
        data={"sub": user.id, "email": user.email}
    )

    return TokenResponse(access_token=access_token, user_id=user.id)


@router.get("/auth/me")
async def get_me(current_user: str = Depends(get_current_user)):
    """Get current user information."""
    return {
        "user_id": current_user,
        "email": "user@example.com"  # Would come from database
    }
