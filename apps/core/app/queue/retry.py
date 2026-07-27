"""Retry mechanism with exponential backoff."""

import asyncio
from typing import Callable, TypeVar, Optional
from functools import wraps
import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """Initialize retry configuration."""
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


class RetryPolicy:
    """Retry policy for different scenarios."""

    # Default policy for general operations
    DEFAULT = RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        max_delay=30.0,
    )

    # Aggressive policy for critical operations
    AGGRESSIVE = RetryConfig(
        max_attempts=5,
        base_delay=0.5,
        max_delay=10.0,
    )

    # Conservative policy for non-critical operations
    CONSERVATIVE = RetryConfig(
        max_attempts=2,
        base_delay=2.0,
        max_delay=60.0,
    )

    # Long-running policy for expensive operations
    LONG_RUNNING = RetryConfig(
        max_attempts=3,
        base_delay=5.0,
        max_delay=300.0,
    )


async def retry_with_backoff(
    func: Callable[..., T],
    config: RetryConfig = RetryPolicy.DEFAULT,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
    *args,
    **kwargs
) -> T:
    """Execute function with exponential backoff retry."""
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            logger.warning(
                "Operation failed, retrying",
                attempt=attempt + 1,
                max_attempts=config.max_attempts,
                error=str(e)
            )
            
            if on_retry:
                on_retry(e, attempt + 1)
            
            # Don't wait after last attempt
            if attempt < config.max_attempts - 1:
                delay = _calculate_delay(attempt, config)
                await asyncio.sleep(delay)
    
    raise last_exception


def _calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay with exponential backoff and jitter."""
    delay = config.base_delay * (config.exponential_base ** attempt)
    delay = min(delay, config.max_delay)
    
    if config.jitter:
        import random
        delay = delay * (0.5 + random.random() * 0.5)
    
    return delay


def retry_decorator(config: RetryConfig = RetryPolicy.DEFAULT):
    """Decorator for retry with backoff."""
    
    def decorator(func: Callable[..., T]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(func, config, None, *args, **kwargs)
        return wrapper
    return decorator


def retry_on_exception(
    exception_types: tuple[type[Exception], ...],
    config: RetryConfig = RetryPolicy.DEFAULT
):
    """Decorator to retry on specific exceptions."""
    
    def decorator(func: Callable[..., T]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exception_types as e:
                    last_exception = e
                    logger.warning(
                        "Operation failed with expected exception, retrying",
                        attempt=attempt + 1,
                        max_attempts=config.max_attempts,
                        error=str(e)
                    )
                    
                    if attempt < config.max_attempts - 1:
                        delay = _calculate_delay(attempt, config)
                        await asyncio.sleep(delay)
                except Exception as e:
                    # Re-raise unexpected exceptions
                    raise
            
            raise last_exception
        
        return wrapper
    return decorator
