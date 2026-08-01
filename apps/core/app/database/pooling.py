"""Database connection pooling configuration."""

import structlog
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

logger = structlog.get_logger(__name__)


def create_pool_engine(pool_size: int = 10, max_overflow: int = 20):
    """Create database engine with optimized pooling."""

    engine = create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_recycle=3600,  # Recycle connections after 1 hour
        pool_timeout=30,  # Timeout for getting connection from pool
        connect_args={
            "server_settings": {
                "jit": "off",  # Disable JIT for predictable performance
                "application_name": "tempus-core",
            }
        },
    )

    logger.info(
        "Database pool configured",
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_recycle=3600,
    )

    return engine


def create_test_engine():
    """Create database engine for testing with NullPool."""

    engine = create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        poolclass=NullPool,  # No pooling for tests
    )

    logger.info("Test database engine configured with NullPool")

    return engine


class PoolMonitor:
    """Monitor database pool health."""

    def __init__(self, engine):
        """Initialize pool monitor."""
        self.engine = engine

    def get_pool_status(self) -> dict:
        """Get current pool status."""
        pool = self.engine.pool

        return {
            "size": pool.size(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "checked_in": pool.checkedin(),
        }

    async def check_pool_health(self) -> dict:
        """Check pool health."""
        status = self.get_pool_status()

        # Calculate health metrics
        utilization = status["checked_out"] / status["size"] if status["size"] > 0 else 0
        overflow_ratio = status["overflow"] / status["size"] if status["size"] > 0 else 0

        health = {
            "status": "healthy",
            "utilization": utilization,
            "overflow_ratio": overflow_ratio,
            "details": status,
        }

        # Determine health status
        if utilization > 0.9:
            health["status"] = "warning"
            health["message"] = "High pool utilization"

        if overflow_ratio > 0.5:
            health["status"] = "critical"
            health["message"] = "High pool overflow"

        return health


__all__ = [
    "create_pool_engine",
    "create_test_engine",
    "PoolMonitor",
]
