"""Time block model."""

from datetime import datetime
from sqlalchemy import DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


class TimeBlock(Base):
    """Time block model representing scheduled time for tasks."""
    
    __tablename__ = "time_blocks"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    block_type: Mapped[str] = mapped_column(String(50), default="focus")  # focus, break, meeting
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="time_blocks")
    task: Mapped["Task"] = relationship("Task", back_populates="time_blocks")
    
    def __repr__(self) -> str:
        return f"<TimeBlock(id={self.id}, title={self.title}, start={self.start_at})>"
