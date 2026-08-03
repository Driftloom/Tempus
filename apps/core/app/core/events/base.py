"""Base classes for event-driven architecture."""

import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime
from typing import Generic, TypeVar

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)

T = TypeVar("T", bound="Event")


class Event(BaseModel):
    """Base event class."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: str = None


class EventHandler(ABC, Generic[T]):
    """Base event handler."""

    @abstractmethod
    async def handle(self, event: T) -> None:
        """Handle the event."""
        pass


class EventBus:
    """Event bus for publishing and subscribing to events."""

    def __init__(self):
        """Initialize event bus."""
        self._handlers: dict[str, list[Callable]] = {}

    def subscribe(self, event_type: type, handler: Callable) -> None:
        """Subscribe to an event type."""
        event_name = event_type.__name__
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)

    def unsubscribe(self, event_type: type, handler: Callable) -> None:
        """Unsubscribe from an event type."""
        event_name = event_type.__name__
        if event_name in self._handlers:
            self._handlers[event_name].remove(handler)

    async def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        event_name = type(event).__name__
        if event_name in self._handlers:
            for handler in self._handlers[event_name]:
                try:
                    await handler(event)
                except Exception as e:
                    pass


# Global event bus instance
event_bus = EventBus()
