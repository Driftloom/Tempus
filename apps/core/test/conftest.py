"""Pytest configuration."""

import os
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Set test environment before importing app modules
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/tempus_test"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["JWT_SECRET"] = "test_secret_key_for_testing_only"
os.environ["ENCRYPTION_KEY"] = "test_encryption_key_for_testing_only"
os.environ["TEMPUS_ENV"] = "test"
os.environ["LOG_LEVEL"] = "DEBUG"

from app.database.models import *  # Import all models
from app.database.session import Base


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    from app.core.config import settings

    engine = create_async_engine(
        settings.database_url.replace("tempus", "tempus_test"),
        echo=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_db(test_engine):
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
