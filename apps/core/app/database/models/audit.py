"""Audit log model."""

from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class AuditLog(Base):
    """Audit log model for security and compliance."""

    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    actor: Mapped[str] = mapped_column(String(50), nullable=False)  # user, system, skill, agent
    actor_id: Mapped[str] = mapped_column(String(36), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # task.create, memory.ingest
    resource_type: Mapped[str] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=True)
    metadata: Mapped[dict] = mapped_column(Text, nullable=True)  # JSON with additional context
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, actor={self.actor})>"
