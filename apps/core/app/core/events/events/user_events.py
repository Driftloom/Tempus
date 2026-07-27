"""User-related events."""

from pydantic import Field
from app.core.events.base import Event


class UserCreatedEvent(Event):
    """Event emitted when a user is created."""
    user_id: str
    email: str


class UserUpdatedEvent(Event):
    """Event emitted when a user is updated."""
    user_id: str
    changes: dict
