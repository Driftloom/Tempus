"""Notification model."""

from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database.session import Base


class NotificationType(str, Enum):
    """Notification type enumeration."""
    TASK_DUE = "task_due"
    TASK_OVERDUE = "task_overdue"
    MEMORY_DIGEST = "memory_digest"
    AGENT_COMPLETE = "agent_complete"
    CONNECTOR_ERROR = "connector_error"


class NotificationStatus(str, Enum):
    """Notification status enumeration."""
    PENDING = "pending"
    SENT = "sent"
    DISMISSED = "dismissed"
    SNOOZED = "snoozed"


class Notification(Base):
    """Notification model representing user notifications."""
    
    __tablename__ = "notifications"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    notification_type: Mapped[NotificationType] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[NotificationStatus] = mapped_column(String(20), default=NotificationStatus.PENDING, nullable=False)
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    snoozed_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    related_task_id: Mapped[str] = mapped_column(String(36), nullable=True)
    related_memory_id: Mapped[str] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type={self.notification_type}, status={self.status})>"
