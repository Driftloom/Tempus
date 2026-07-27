"""Structured logging configuration."""

import structlog
from app.core.config import settings


def configure_logging():
    """Configure structured logging with structlog."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    logger = structlog.get_logger()
    logger.info("Structured logging configured", level=settings.log_level)
    return logger


def get_logger(name: str):
    """Get a logger instance."""
    return structlog.get_logger(name)
