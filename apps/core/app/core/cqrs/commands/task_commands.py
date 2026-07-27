"""Task commands."""

from pydantic import Field
from app.core.cqrs.base import Command
from datetime import datetime
from typing import Optional


class CreateTaskCommand(Command):
    """Command to create a task."""
    user_id: str
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_at: Optional[datetime] = None
    source: str = "manual"


class UpdateTaskCommand(Command):
    """Command to update a task."""
    task_id: str
    user_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_at: Optional[datetime] = None


class DeleteTaskCommand(Command):
    """Command to delete a task."""
    task_id: str
    user_id: str


class CompleteTaskCommand(Command):
    """Command to complete a task."""
    task_id: str
    user_id: str
