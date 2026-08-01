"""Agent run models for agent execution tracking."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.session import Base


class AgentRunStatus(str, Enum):
    """Status of an agent run."""
    RUNNING = "running"
    COMPLETED = "completed"
    BUDGET_EXHAUSTED = "budget_exhausted"
    ERROR = "error"
    CANCELLED = "cancelled"


class AgentRunStepType(str, Enum):
    """Type of agent run step."""
    PLAN = "plan"
    ACT = "act"
    OBSERVE = "observe"
    REFLECT = "reflect"


class AgentRun(Base):
    """Agent run execution tracking."""
    __tablename__ = "agent_runs"

    id = Column(String, primary_key=True, index=True)
    agent_type = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    goal = Column(Text, nullable=False)
    status = Column(String, nullable=False, default=AgentRunStatus.RUNNING, index=True)

    # Budget tracking
    current_step_index = Column(Integer, default=0)
    budget_max_steps = Column(Integer, nullable=False)
    budget_max_duration_s = Column(Integer, nullable=True)
    budget_max_cost_usd = Column(Float, nullable=True)
    cost_used_usd = Column(Float, default=0.0)

    # Timestamps
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Results
    result_summary = Column(Text, nullable=True)
    error_reason = Column(Text, nullable=True)

    # Relationships
    steps = relationship("AgentRunStep", back_populates="agent_run", cascade="all, delete-orphan")


class AgentRunStep(Base):
    """Individual step in an agent run."""
    __tablename__ = "agent_run_steps"

    id = Column(String, primary_key=True, index=True)
    agent_run_id = Column(String, ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    step_index = Column(Integer, nullable=False)
    step_type = Column(String, nullable=False)

    # Step content
    content = Column(Text, nullable=True)
    tool_called = Column(String, nullable=True)
    tool_result = Column(Text, nullable=True)

    # Cost tracking
    cost_usd = Column(Float, default=0.0)

    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    agent_run = relationship("AgentRun", back_populates="steps")
