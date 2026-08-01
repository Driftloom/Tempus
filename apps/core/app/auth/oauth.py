"""OAuth2 flow handler for connector authentication."""


from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request, status
from structlog import get_logger

logger = get_logger(__name__)


class OAuth2Handler:
    """Handler for OAuth2 authentication flows."""

    def __init__(self):
        """Initialize OAuth2 handler."""
        self.oauth = OAuth()
        self._setup_providers()

    def _setup_providers(self):
        """Setup OAuth2 providers."""
        # Google/Gmail OAuth2
        google_config = {
            "client_id": "GOOGLE_CLIENT_ID",  # Will be loaded from env
            "client_secret": "GOOGLE_CLIENT_SECRET",
            "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
            "client_kwargs": {
                "scope": "openid email profile https://www.googleapis.com/auth/gmail.readonly"
            }
        }
        self.oauth.register(
            name="google",
            client_id=google_config["client_id"],
            client_secret=google_config["client_secret"],
            server_metadata_url=google_config["server_metadata_url"],
            client_kwargs=google_config["client_kwargs"]
        )

    async def initiate_oauth_flow(
        self,
        provider: str,
        redirect_uri: str,
        state: str | None = None
    ) -> str:
        """Initiate OAuth2 flow and return authorization URL."""
        if provider not in self.oauth._registry:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}"
            )

        client = self.oauth.create_client(provider)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create OAuth client for {provider}"
            )

        # Generate authorization URL
        authorization_url = await client.authorize_redirect(
            redirect_uri,
            state=state
        )

        logger.info("OAuth flow initiated", provider=provider, redirect_uri=redirect_uri)
        return authorization_url

    async def handle_oauth_callback(
        self,
        provider: str,
        request: Request
    ) -> dict:
        """Handle OAuth2 callback and return tokens."""
        if provider not in self.oauth._registry:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}"
            )

        client = self.oauth.create_client(provider)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create OAuth client for {provider}"
            )

        try:
            # Exchange authorization code for tokens
            token = await client.authorize_access_token(request)

            logger.info("OAuth callback successful", provider=provider)

            return {
                "access_token": token.get("access_token"),
                "refresh_token": token.get("refresh_token"),
                "token_type": token.get("token_type", "Bearer"),
                "expires_in": token.get("expires_in"),
                "scope": token.get("scope")
            }
        except Exception as e:
            logger.error("OAuth callback failed", provider=provider, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code for tokens"
            )

    async def refresh_token(
        self,
        provider: str,
        refresh_token: str
    ) -> dict:
        """Refresh an expired OAuth2 token."""
        if provider not in self.oauth._registry:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}"
            )

        client = self.oauth.create_client(provider)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create OAuth client for {provider}"
            )

        try:
            # Refresh the token
            token = await client.refresh_token(refresh_token)

            logger.info("Token refresh successful", provider=provider)

            return {
                "access_token": token.get("access_token"),
                "refresh_token": token.get("refresh_token"),
                "token_type": token.get("token_type", "Bearer"),
                "expires_in": token.get("expires_in"),
                "scope": token.get("scope")
            }
        except Exception as e:
            logger.error("Token refresh failed", provider=provider, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to refresh token"
            )


# Global OAuth2 handler instance
oauth_handler = OAuth2Handler()
