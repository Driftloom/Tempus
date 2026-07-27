"""Memory-related events."""

from pydantic import Field
from app.core.events.base import Event


class MemoryCreatedEvent(Event):
    """Event emitted when a memory is created."""
    memory_id: str
    user_id: str
    layer: str
    provenance: str


class MemoryUpdatedEvent(Event):
    """Event emitted when a memory is updated."""
    memory_id: str
    user_id: str
    changes: dict


class MemoryDeletedEvent(Event):
    """Event emitted when a memory is deleted."""
    memory_id: str
    user_id: str


class MemoryConsolidatedEvent(Event):
    """Event emitted when memory is consolidated."""
    user_id: str
    memories_consolidated: int
