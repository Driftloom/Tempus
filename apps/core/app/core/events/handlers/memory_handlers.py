"""Memory event handlers."""

from app.core.events.base import EventHandler
from app.core.events.events.memory_events import (
    MemoryCreatedEvent,
    MemoryUpdatedEvent,
    MemoryDeletedEvent,
    MemoryConsolidatedEvent,
)
import structlog

logger = structlog.get_logger(__name__)


class MemoryEventHandler(EventHandler[MemoryCreatedEvent]):
    """Handler for memory events."""

    async def handle(self, event: MemoryCreatedEvent | MemoryUpdatedEvent | MemoryDeletedEvent | MemoryConsolidatedEvent) -> None:
        """Handle memory event."""
        event_type = type(event).__name__
        
        if isinstance(event, MemoryCreatedEvent):
            await self._handle_created(event)
        elif isinstance(event, MemoryUpdatedEvent):
            await self._handle_updated(event)
        elif isinstance(event, MemoryDeletedEvent):
            await self._handle_deleted(event)
        elif isinstance(event, MemoryConsolidatedEvent):
            await self._handle_consolidated(event)
    
    async def _handle_created(self, event: MemoryCreatedEvent) -> None:
        """Handle memory created event."""
        logger.info("Memory created", memory_id=event.memory_id, user_id=event.user_id, layer=event.layer)
        # Trigger embedding generation
        # Update memory statistics
    
    async def _handle_updated(self, event: MemoryUpdatedEvent) -> None:
        """Handle memory updated event."""
        logger.info("Memory updated", memory_id=event.memory_id, user_id=event.user_id, changes=event.changes)
        # Re-generate embeddings if content changed
        # Update memory statistics
    
    async def _handle_deleted(self, event: MemoryDeletedEvent) -> None:
        """Handle memory deleted event."""
        logger.info("Memory deleted", memory_id=event.memory_id, user_id=event.user_id)
        # Update memory statistics
    
    async def _handle_consolidated(self, event: MemoryConsolidatedEvent) -> None:
        """Handle memory consolidated event."""
        logger.info("Memory consolidated", user_id=event.user_id, count=event.memories_consolidated)
        # Update memory statistics
        # Log to analytics
