"""Event definitions."""

from app.core.events.events.task_events import (
    TaskCreatedEvent,
    TaskUpdatedEvent,
    TaskDeletedEvent,
    TaskCompletedEvent,
)
from app.core.events.events.memory_events import (
    MemoryCreatedEvent,
    MemoryUpdatedEvent,
    MemoryDeletedEvent,
    MemoryConsolidatedEvent,
)
from app.core.events.events.user_events import (
    UserCreatedEvent,
    UserUpdatedEvent,
)

__all__ = [
    "TaskCreatedEvent",
    "TaskUpdatedEvent",
    "TaskDeletedEvent",
    "TaskCompletedEvent",
    "MemoryCreatedEvent",
    "MemoryUpdatedEvent",
    "MemoryDeletedEvent",
    "MemoryConsolidatedEvent",
    "UserCreatedEvent",
    "UserUpdatedEvent",
]
