"""Connector models."""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class ConnectorType(str, Enum):
    """Connector type enumeration."""
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    CALENDAR = "calendar"
    SLACK = "slack"
    GITHUB = "github"


class ConnectorStatus(str, Enum):
    """Connector status enumeration."""
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


class Connector(Base):
    """Connector model representing an external service connection."""

    __tablename__ = "connectors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    connector_type: Mapped[ConnectorType] = mapped_column(String(50), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[ConnectorStatus] = mapped_column(String(20), default=ConnectorStatus.ACTIVE, nullable=False)
    last_sync_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Connector(id={self.id}, type={self.connector_type}, status={self.status})>"


class ConnectorCredential(Base):
    """Connector credential model storing encrypted tokens."""

    __tablename__ = "connector_credentials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    connector_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    credential_type: Mapped[str] = mapped_column(String(50), nullable=False)  # oauth_token, api_key
    encrypted_token: Mapped[str] = mapped_column(Text, nullable=False)  # Encrypted token
    token_metadata: Mapped[dict] = mapped_column(Text, nullable=True)  # JSON with expiry, scopes, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ConnectorCredential(id={self.id}, connector_id={self.connector_id})>"
