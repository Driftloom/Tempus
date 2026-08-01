"""Rate limiting for API endpoints."""

from fastapi import HTTPException, Request, status
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from structlog import get_logger

logger = get_logger(__name__)

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)


def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded."""
    logger.warning("Rate limit exceeded", path=request.url.path, client=get_remote_address(request))
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Rate limit exceeded"
    )
