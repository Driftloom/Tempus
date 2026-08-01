"""Celery tasks for notification processing."""

from structlog import get_logger

from app.database.session import AsyncSessionLocal
from app.notifications.scheduler.celery_app import celery_app
from app.notifications.service import NotificationService

logger = get_logger(__name__)
notification_service = NotificationService()


@celery_app.task(name="send_notification")
def send_notification(notification_id: str):
    """Send a notification to the user."""
    logger.info("Sending notification", notification_id=notification_id)

    # In production, would send via WebSocket to client
    # For now, just log
    logger.info("Notification sent", notification_id=notification_id)

    # Mark as sent in database
    import asyncio
    asyncio.run(_mark_sent(notification_id))


async def _mark_sent(notification_id: str):
    """Mark notification as sent in database."""
    async with AsyncSessionLocal() as db:
        await notification_service.mark_sent(db, notification_id)


@celery_app.task(name="process_due_notifications")
def process_due_notifications():
    """Process all notifications that are due."""
    logger.info("Processing due notifications")

    # In production, would query for due notifications and send them
    # For now, just log
    logger.info("Due notifications processed")


@celery_app.task(name="escalate_unacknowledged")
def escalate_unacknowledged():
    """Escalate unacknowledged notifications."""
    logger.info("Escalating unacknowledged notifications")

    # In production, would check for notifications past due and escalate
    # For now, just log
    logger.info("Escalation completed")
