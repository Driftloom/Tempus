"""Task-related events."""

from datetime import datetime

from pydantic import Field

from app.core.events.base import Event


class TaskCreatedEvent(Event):
    """Event emitted when a task is created."""
    task_id: str
    user_id: str
    title: str
    priority: str


class TaskUpdatedEvent(Event):
    """Event emitted when a task is updated."""
    task_id: str
    user_id: str
    changes: dict


class TaskDeletedEvent(Event):
    """Event emitted when a task is deleted."""
    task_id: str
    user_id: str


class TaskCompletedEvent(Event):
    """Event emitted when a task is completed."""
    task_id: str
    user_id: str
    completed_at: datetime = Field(default_factory=datetime.utcnow)
