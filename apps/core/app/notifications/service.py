"""Notification service with Celery scheduler integration."""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models.notification import Notification, NotificationType, NotificationStatus
from app.database.repositories.base import BaseRepository
from structlog import get_logger

logger = get_logger(__name__)


class NotificationService:
    """Service for managing notifications with Celery scheduling."""
    
    def __init__(self):
        """Initialize notification service."""
        self.notification_repo = BaseRepository(Notification, dict, dict)
    
    async def create_notification(
        self,
        db: AsyncSession,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        body: Optional[str],
        scheduled_for: datetime,
        related_task_id: Optional[str] = None,
        related_memory_id: Optional[str] = None
    ) -> Notification:
        """Create a new notification and schedule it."""
        logger.info("Creating notification", user_id=user_id, type=notification_type)
        
        notification_data = {
            "user_id": user_id,
            "notification_type": notification_type,
            "title": title,
            "body": body,
            "status": NotificationStatus.PENDING,
            "scheduled_for": scheduled_for,
            "related_task_id": related_task_id,
            "related_memory_id": related_memory_id
        }
        
        notification = await self.notification_repo.create(db, notification_data)
        
        # Schedule Celery task for notification delivery
        self._schedule_notification(notification.id, scheduled_for)
        
        logger.info("Notification created and scheduled", notification_id=notification.id)
        return notification
    
    async def get_pending_notifications(
        self,
        db: AsyncSession,
        user_id: str
    ) -> List[Notification]:
        """Get pending notifications for user."""
        result = await db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.status == NotificationStatus.PENDING,
                Notification.scheduled_for <= datetime.utcnow()
            )
        )
        return result.scalars().all()
    
    async def get_due_notifications(self, db: AsyncSession) -> List[Notification]:
        """Get all notifications due for delivery."""
        result = await db.execute(
            select(Notification).where(
                Notification.status == NotificationStatus.PENDING,
                Notification.scheduled_for <= datetime.utcnow()
            )
        )
        return result.scalars().all()
    
    async def mark_sent(
        self,
        db: AsyncSession,
        notification_id: str
    ) -> Optional[Notification]:
        """Mark notification as sent."""
        notification = await self.notification_repo.get(db, notification_id)
        if notification:
            updates = {
                "status": NotificationStatus.SENT,
                "sent_at": datetime.utcnow()
            }
            updated = await self.notification_repo.update(db, notification, updates)
            logger.info("Notification marked sent", notification_id=notification_id)
            return updated
        return None
    
    async def dismiss(
        self,
        db: AsyncSession,
        notification_id: str
    ) -> Optional[Notification]:
        """Dismiss a notification."""
        notification = await self.notification_repo.get(db, notification_id)
        if notification:
            updates = {"status": NotificationStatus.DISMISSED}
            updated = await self.notification_repo.update(db, notification, updates)
            logger.info("Notification dismissed", notification_id=notification_id)
            return updated
        return None
    
    async def snooze(
        self,
        db: AsyncSession,
        notification_id: str,
        minutes: int = 10
    ) -> Optional[Notification]:
        """Snooze a notification."""
        notification = await self.notification_repo.get(db, notification_id)
        if notification:
            snooze_until = datetime.utcnow() + timedelta(minutes=minutes)
            updates = {
                "status": NotificationStatus.SNOOZED,
                "snoozed_until": snooze_until,
                "scheduled_for": snooze_until
            }
            updated = await self.notification_repo.update(db, notification, updates)
            
            # Reschedule Celery task
            self._schedule_notification(notification_id, snooze_until)
            
            logger.info("Notification snoozed", notification_id=notification_id, minutes=minutes)
            return updated
        return None
    
    async def escalate(
        self,
        db: AsyncSession,
        notification_id: str,
        escalation_level: int = 1
    ) -> Optional[Notification]:
        """Escalate a notification to higher priority."""
        notification = await self.notification_repo.get(db, notification_id)
        if notification:
            updates = {
                "escalation_level": escalation_level,
                "escalated_at": datetime.utcnow()
            }
            updated = await self.notification_repo.update(db, notification, updates)
            logger.info("Notification escalated", notification_id=notification_id, level=escalation_level)
            return updated
        return None
    
    def _schedule_notification(self, notification_id: str, scheduled_for: datetime):
        """Schedule notification delivery via Celery."""
        try:
            from app.notifications.tasks import deliver_notification
            from datetime import timezone
            
            # Calculate delay in seconds
            now = datetime.utcnow().replace(tzinfo=timezone.utc)
            scheduled = scheduled_for.replace(tzinfo=timezone.utc)
            delay_seconds = max(0, (scheduled - now).total_seconds())
            
            # Schedule Celery task
            deliver_notification.apply_async(
                args=[notification_id],
                countdown=delay_seconds
            )
            
            logger.info("Celery task scheduled", notification_id=notification_id, delay_seconds=delay_seconds)
        except ImportError:
            logger.warning("Celery not available, notification not scheduled", notification_id=notification_id)
        except Exception as e:
            logger.error("Failed to schedule Celery task", notification_id=notification_id, error=str(e))
