"""Celery tasks for notification delivery."""

from celery import shared_task
from app.notifications.service import NotificationService
from app.database.session import AsyncSessionLocal
import structlog

logger = structlog.get_logger(__name__)


@shared_task(bind=True, max_retries=5)
def deliver_notification(self, notification_id: str):
    """Deliver a notification to the user."""
    logger.info("Delivering notification", notification_id=notification_id)
    
    try:
        async def _deliver():
            async with AsyncSessionLocal() as db:
                notification_service = NotificationService(db)
                await notification_service.deliver(notification_id)
        
        import asyncio
        asyncio.run(_deliver())
        logger.info("Notification delivered", notification_id=notification_id)
        return {"status": "success", "notification_id": notification_id}
    
    except Exception as e:
        logger.error("Notification delivery failed", notification_id=notification_id, error=str(e))
        # Exponential backoff: 1min, 2min, 4min, 8min, 16min
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task
def escalate_notification(notification_id: str):
    """Escalate a notification to the next level."""
    logger.info("Escalating notification", notification_id=notification_id)
    
    try:
        async def _escalate():
            async with AsyncSessionLocal() as db:
                notification_service = NotificationService(db)
                await notification_service.escalate(notification_id)
        
        import asyncio
        asyncio.run(_escalate())
        logger.info("Notification escalated", notification_id=notification_id)
        return {"status": "success", "notification_id": notification_id}
    
    except Exception as e:
        logger.error("Notification escalation failed", notification_id=notification_id, error=str(e))
        raise


@shared_task
def schedule_notifications():
    """Schedule notifications that are due."""
    logger.info("Scheduling notifications")
    
    try:
        async def _schedule():
            async with AsyncSessionLocal() as db:
                notification_service = NotificationService(db)
                await notification_service.schedule_due_notifications()
        
        import asyncio
        asyncio.run(_schedule())
        logger.info("Notifications scheduled")
        return {"status": "success"}
    
    except Exception as e:
        logger.error("Notification scheduling failed", error=str(e))
        raise
