"""Memory models."""

from datetime import datetime
from enum import Enum

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class MemoryLayer(str, Enum):
    """Memory layer enumeration."""
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class MemorySensitivity(str, Enum):
    """Memory sensitivity enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MemoryProvenance(str, Enum):
    """Memory provenance enumeration for security tracking."""
    USER_DIRECT = "user_direct"
    INTERNAL_MEMORY = "internal_memory"
    EXTERNAL_UNTRUSTED_EMAIL = "external_untrusted:email"
    EXTERNAL_UNTRUSTED_WEB = "external_untrusted:web"
    EXTERNAL_UNTRUSTED_CONNECTOR = "external_untrusted:connector"


class MemoryItem(Base):
    """Memory item model representing a piece of stored information."""

    __tablename__ = "memory_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    layer: Mapped[MemoryLayer] = mapped_column(String(20), nullable=False, index=True)
    sensitivity: Mapped[MemorySensitivity] = mapped_column(String(20), default=MemorySensitivity.MEDIUM, nullable=False, index=True)
    importance_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=True)  # user_direct, email, browser
    source_ref: Mapped[str] = mapped_column(String(255), nullable=True)
    provenance: Mapped[str] = mapped_column(String(100), default="user_direct", nullable=False, index=True)  # Security tracking
    tags: Mapped[dict] = mapped_column(Text, nullable=True)  # JSON array
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    ttl_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)  # For working memory

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="memory_items")
    edges_from: Mapped[list["MemoryEdge"]] = relationship("MemoryEdge", foreign_keys="MemoryEdge.from_memory_id", back_populates="from_memory")
    edges_to: Mapped[list["MemoryEdge"]] = relationship("MemoryEdge", foreign_keys="MemoryEdge.to_memory_id", back_populates="to_memory")

    def __repr__(self) -> str:
        return f"<MemoryItem(id={self.id}, layer={self.layer}, sensitivity={self.sensitivity})>"


class MemoryEdge(Base):
    """Memory edge model representing relationships between memory items."""

    __tablename__ = "memory_edges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    from_memory_id: Mapped[str] = mapped_column(String(36), ForeignKey("memory_items.id"), nullable=False, index=True)
    to_memory_id: Mapped[str] = mapped_column(String(36), ForeignKey("memory_items.id"), nullable=False, index=True)
    edge_type: Mapped[str] = mapped_column(String(50), nullable=False)  # related, caused_by, similar_to
    strength: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    from_memory: Mapped["MemoryItem"] = relationship("MemoryItem", foreign_keys=[from_memory_id], back_populates="edges_from")
    to_memory: Mapped["MemoryItem"] = relationship("MemoryItem", foreign_keys=[to_memory_id], back_populates="edges_to")

    def __repr__(self) -> str:
        return f"<MemoryEdge(from={self.from_memory_id}, to={self.to_memory_id}, type={self.edge_type})>"
