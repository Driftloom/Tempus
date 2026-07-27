"""Celery tasks for email processing."""

from celery import shared_task
from app.email.service import EmailService
from app.database.session import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

logger = structlog.get_logger(__name__)


@shared_task(bind=True, max_retries=3)
def process_email_sync(self, user_id: str, connector_id: str):
    """Process email synchronization for a connector."""
    logger.info("Processing email sync", user_id=user_id, connector_id=connector_id)
    
    try:
        async def _process():
            async with AsyncSessionLocal() as db:
                email_service = EmailService(db)
                await email_service.sync_emails(user_id, connector_id)
        
        import asyncio
        asyncio.run(_process())
        logger.info("Email sync completed", user_id=user_id, connector_id=connector_id)
        return {"status": "success", "user_id": user_id, "connector_id": connector_id}
    
    except Exception as e:
        logger.error("Email sync failed", user_id=user_id, connector_id=connector_id, error=str(e))
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task
def classify_email(email_id: str):
    """Classify an email using AI."""
    logger.info("Classifying email", email_id=email_id)
    
    try:
        async def _classify():
            async with AsyncSessionLocal() as db:
                email_service = EmailService(db)
                await email_service.classify_email(email_id)
        
        import asyncio
        asyncio.run(_classify())
        logger.info("Email classified", email_id=email_id)
        return {"status": "success", "email_id": email_id}
    
    except Exception as e:
        logger.error("Email classification failed", email_id=email_id, error=str(e))
        raise


@shared_task
def extract_entities_from_email(email_id: str):
    """Extract entities from an email."""
    logger.info("Extracting entities from email", email_id=email_id)
    
    try:
        async def _extract():
            async with AsyncSessionLocal() as db:
                email_service = EmailService(db)
                await email_service.extract_entities(email_id)
        
        import asyncio
        asyncio.run(_extract())
        logger.info("Entities extracted from email", email_id=email_id)
        return {"status": "success", "email_id": email_id}
    
    except Exception as e:
        logger.error("Entity extraction failed", email_id=email_id, error=str(e))
        raise
