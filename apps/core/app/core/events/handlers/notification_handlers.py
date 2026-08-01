"""Notification event handlers."""

import structlog

from app.core.events.base import EventHandler
from app.core.events.events.memory_events import MemoryCreatedEvent
from app.core.events.events.task_events import TaskCompletedEvent, TaskCreatedEvent

logger = structlog.get_logger(__name__)


class NotificationEventHandler(EventHandler[TaskCreatedEvent]):
    """Handler for notification events."""

    async def handle(self, event: TaskCreatedEvent | TaskCompletedEvent | MemoryCreatedEvent) -> None:
        """Handle notification event."""
        event_type = type(event).__name__

        if isinstance(event, TaskCreatedEvent):
            await self._handle_task_created(event)
        elif isinstance(event, TaskCompletedEvent):
            await self._handle_task_completed(event)
        elif isinstance(event, MemoryCreatedEvent):
            await self._handle_memory_created(event)

    async def _handle_task_created(self, event: TaskCreatedEvent) -> None:
        """Handle task created notification."""
        logger.info("Task created notification", task_id=event.task_id, user_id=event.user_id)
        # Create notification for user
        # Schedule notification delivery

    async def _handle_task_completed(self, event: TaskCompletedEvent) -> None:
        """Handle task completed notification."""
        logger.info("Task completed notification", task_id=event.task_id, user_id=event.user_id)
        # Create notification for user
        # Schedule notification delivery

    async def _handle_memory_created(self, event: MemoryCreatedEvent) -> None:
        """Handle memory created notification."""
        logger.info("Memory created notification", memory_id=event.memory_id, user_id=event.user_id)
        # Create notification if memory is important
        # Schedule notification delivery
