"""Base classes for CQRS pattern."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R")


class Command(BaseModel):
    """Base command class."""
    pass


class Query(BaseModel):
    """Base query class."""
    pass


class CommandHandler(ABC, Generic[T, R]):
    """Base command handler."""

    @abstractmethod
    async def handle(self, command: T) -> R:
        """Handle the command."""
        pass


class QueryHandler(ABC, Generic[T, R]):
    """Base query handler."""

    @abstractmethod
    async def handle(self, query: T) -> R:
        """Handle the query."""
        pass
