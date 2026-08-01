"""Task event handlers."""

import structlog

from app.core.events.base import EventHandler
from app.core.events.events.task_events import (
    TaskCompletedEvent,
    TaskCreatedEvent,
    TaskDeletedEvent,
    TaskUpdatedEvent,
)

logger = structlog.get_logger(__name__)


class TaskEventHandler(EventHandler[TaskCreatedEvent]):
    """Handler for task events."""

    async def handle(self, event: TaskCreatedEvent | TaskUpdatedEvent | TaskDeletedEvent | TaskCompletedEvent) -> None:
        """Handle task event."""
        event_type = type(event).__name__

        if isinstance(event, TaskCreatedEvent):
            await self._handle_created(event)
        elif isinstance(event, TaskUpdatedEvent):
            await self._handle_updated(event)
        elif isinstance(event, TaskDeletedEvent):
            await self._handle_deleted(event)
        elif isinstance(event, TaskCompletedEvent):
            await self._handle_completed(event)

    async def _handle_created(self, event: TaskCreatedEvent) -> None:
        """Handle task created event."""
        logger.info("Task created", task_id=event.task_id, user_id=event.user_id)
        # Trigger notification for new task
        # Update user statistics
        # Log to analytics

    async def _handle_updated(self, event: TaskUpdatedEvent) -> None:
        """Handle task updated event."""
        logger.info("Task updated", task_id=event.task_id, user_id=event.user_id, changes=event.changes)
        # Trigger notification if priority changed
        # Update user statistics

    async def _handle_deleted(self, event: TaskDeletedEvent) -> None:
        """Handle task deleted event."""
        logger.info("Task deleted", task_id=event.task_id, user_id=event.user_id)
        # Update user statistics
        # Log to analytics

    async def _handle_completed(self, event: TaskCompletedEvent) -> None:
        """Handle task completed event."""
        logger.info("Task completed", task_id=event.task_id, user_id=event.user_id)
        # Trigger completion notification
        # Update user statistics
        # Potentially trigger memory consolidation
