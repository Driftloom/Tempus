"""Unit tests for base repository functionality."""

import pytest
from pydantic import BaseModel
from app.database.repositories.base import BaseRepository


class MockModel:
    """Mock model for testing."""

    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name


class MockCreateSchema(BaseModel):
    """Mock create schema."""
    name: str


class MockUpdateSchema(BaseModel):
    """Mock update schema."""
    name: str | None = None


class MockRepository(BaseRepository[MockModel, MockCreateSchema, MockUpdateSchema]):
    """Mock repository for testing."""

    def __init__(self):
        super().__init__(MockModel)


def test_base_repository_initialization():
    """Test repository initialization."""
    repo = MockRepository()
    assert repo.model == MockModel


def test_base_repository_has_required_methods():
    """Test that repository has required methods."""
    repo = MockRepository()
    assert hasattr(repo, 'get')
    assert hasattr(repo, 'get_multi')
    assert hasattr(repo, 'create')
    assert hasattr(repo, 'update')
    assert hasattr(repo, 'delete')
    assert callable(repo.get)
    assert callable(repo.get_multi)
    assert callable(repo.create)
    assert callable(repo.update)
    assert callable(repo.delete)
