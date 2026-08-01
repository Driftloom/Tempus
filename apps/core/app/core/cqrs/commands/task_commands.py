"""Task commands."""

from datetime import datetime

from app.core.cqrs.base import Command


class CreateTaskCommand(Command):
    """Command to create a task."""
    user_id: str
    title: str
    description: str | None = None
    priority: str = "medium"
    due_at: datetime | None = None
    source: str = "manual"


class UpdateTaskCommand(Command):
    """Command to update a task."""
    task_id: str
    user_id: str
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    due_at: datetime | None = None


class DeleteTaskCommand(Command):
    """Command to delete a task."""
    task_id: str
    user_id: str


class CompleteTaskCommand(Command):
    """Command to complete a task."""
    task_id: str
    user_id: str
