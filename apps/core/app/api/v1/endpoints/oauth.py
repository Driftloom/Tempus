"""OAuth2 endpoints for connector authentication."""


from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from structlog import get_logger

from app.auth.oauth import oauth_handler

logger = get_logger(__name__)

router = APIRouter()


class OAuthInitiateRequest(BaseModel):
    """Request to initiate OAuth flow."""
    provider: str
    redirect_uri: str
    state: str | None = None


class OAuthInitiateResponse(BaseModel):
    """Response with authorization URL."""
    authorization_url: str
    state: str | None


class OAuthCallbackResponse(BaseModel):
    """Response with OAuth tokens."""
    access_token: str
    refresh_token: str | None
    token_type: str
    expires_in: int | None
    scope: str | None


class OAuthRefreshRequest(BaseModel):
    """Request to refresh OAuth token."""
    provider: str
    refresh_token: str


@router.post("/initiate", response_model=OAuthInitiateResponse)
async def initiate_oauth_flow(request: OAuthInitiateRequest):
    """Initiate OAuth2 flow for a connector."""
    try:
        authorization_url = await oauth_handler.initiate_oauth_flow(
            provider=request.provider,
            redirect_uri=request.redirect_uri,
            state=request.state
        )

        return OAuthInitiateResponse(
            authorization_url=authorization_url,
            state=request.state
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to initiate OAuth flow", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate OAuth flow"
        )


@router.get("/callback/{provider}", response_model=OAuthCallbackResponse)
async def handle_oauth_callback(provider: str, request: Request):
    """Handle OAuth2 callback from provider."""
    try:
        tokens = await oauth_handler.handle_oauth_callback(provider, request)

        return OAuthCallbackResponse(**tokens)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to handle OAuth callback", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to handle OAuth callback"
        )


@router.post("/refresh", response_model=OAuthCallbackResponse)
async def refresh_oauth_token(request: OAuthRefreshRequest):
    """Refresh an expired OAuth2 token."""
    try:
        tokens = await oauth_handler.refresh_token(
            provider=request.provider,
            refresh_token=request.refresh_token
        )

        return OAuthCallbackResponse(**tokens)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to refresh OAuth token", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh OAuth token"
        )
