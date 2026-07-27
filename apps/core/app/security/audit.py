"""Audit logging for security events."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.audit import AuditLog
from app.database.repositories.base import BaseRepository
from structlog import get_logger

logger = get_logger(__name__)


class AuditLogger:
    """Logger for security audit events."""
    
    def __init__(self):
        """Initialize audit logger."""
        self.audit_repo = BaseRepository(AuditLog, dict, dict)
    
    async def log(
        self,
        db: AsyncSession,
        user_id: Optional[str],
        actor: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log an audit event."""
        logger.info(
            "Audit log",
            user_id=user_id,
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id
        )
        
        audit_data = {
            "user_id": user_id,
            "actor": actor,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "metadata": metadata,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        await self.audit_repo.create(db, audit_data)
