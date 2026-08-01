"""Circuit breaker pattern for fault tolerance."""

import asyncio
from collections.abc import Callable
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import TypeVar

import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service has recovered


class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 60.0,
        expected_exception: tuple[type[Exception], ...] = (Exception,)
    ) -> None:
        """Initialize circuit breaker configuration."""
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout  # Seconds to wait before trying again
        self.expected_exception = expected_exception


class CircuitBreaker:
    """Circuit breaker implementation."""

    def __init__(self, config: CircuitBreakerConfig) -> None:
        """Initialize circuit breaker."""
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: datetime | None = None
        self._lock = asyncio.Lock()

    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection."""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)

            async with self._lock:
                if self.state == CircuitState.HALF_OPEN:
                    self.success_count += 1
                    if self.success_count >= self.config.success_threshold:
                        self.state = CircuitState.CLOSED
                        self.failure_count = 0
                        self.success_count = 0
                        logger.info("Circuit breaker reset to CLOSED")
                elif self.state == CircuitState.CLOSED:
                    self.failure_count = 0

            return result

        except self.config.expected_exception:
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = datetime.utcnow()

                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitState.OPEN
                    logger.error(
                        "Circuit breaker opened",
                        failure_count=self.failure_count,
                        threshold=self.config.failure_threshold
                    )

            raise

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        if self.last_failure_time is None:
            return True

        time_since_failure = datetime.utcnow() - self.last_failure_time
        return time_since_failure.total_seconds() >= self.config.timeout

    def get_state(self) -> CircuitState:
        """Get current circuit breaker state."""
        return self.state

    def get_metrics(self) -> dict:
        """Get circuit breaker metrics."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
        }


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# Pre-configured circuit breakers
default_circuit_breaker = CircuitBreaker(CircuitBreakerConfig())
aggressive_circuit_breaker = CircuitBreaker(
    CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=1,
        timeout=30.0
    )
)
conservative_circuit_breaker = CircuitBreaker(
    CircuitBreakerConfig(
        failure_threshold=10,
        success_threshold=3,
        timeout=120.0
    )
)


def circuit_breaker_decorator(circuit_breaker: CircuitBreaker = default_circuit_breaker):
    """Decorator for circuit breaker protection."""

    def decorator(func: Callable[..., T]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await circuit_breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator
