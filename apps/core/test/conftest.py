"""Pytest configuration."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

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
