"""Rate limiting middleware for API endpoints."""

import time
from collections import defaultdict
from functools import wraps
from typing import Callable

from fastapi import HTTPException, Request, status
from structlog import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter using token bucket algorithm."""

    def __init__(self, requests_per_minute: int = 60):
        """Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute per user/IP
        """
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for identifier.
        
        Args:
            identifier: User ID or IP address
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        minute_ago = now - 60

        # Clean up old requests
        self.requests[identifier] = [
            timestamp for timestamp in self.requests[identifier]
            if timestamp > minute_ago
        ]

        # Check if under limit
        if len(self.requests[identifier]) >= self.requests_per_minute:
            logger.warning("Rate limit exceeded", identifier=identifier)
            return False

        # Record this request
        self.requests[identifier].append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60)


def rate_limit(requests_per_minute: int = 60):
    """Decorator for rate limiting endpoints.
    
    Args:
        requests_per_minute: Maximum requests per minute
    """
    limiter = RateLimiter(requests_per_minute)

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to get identifier from request (if available in kwargs)
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if request:
                # Use user ID from JWT if available, otherwise use IP
                identifier = request.headers.get("X-User-ID", request.client.host)
                
                if not limiter.is_allowed(identifier):
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Please try again later.",
                        headers={"Retry-After": "60"}
                    )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
