"""Memory commands."""

from pydantic import Field
from app.core.cqrs.base import Command
from typing import Optional


class CreateMemoryCommand(Command):
    """Command to create a memory."""
    user_id: str
    content: str
    layer: str = "short_term"
    provenance: str = "manual"
    importance_score: float = 0.5


class UpdateMemoryCommand(Command):
    """Command to update a memory."""
    memory_id: str
    user_id: str
    content: Optional[str] = None
    layer: Optional[str] = None
    importance_score: Optional[float] = None


class DeleteMemoryCommand(Command):
    """Command to delete a memory."""
    memory_id: str
    user_id: str


class ConsolidateMemoryCommand(Command):
    """Command to consolidate memory."""
    user_id: str
