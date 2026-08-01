"""Agent state store for persistence."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.database.models.agent_runs import AgentRun, AgentRunStatus, AgentRunStep

logger = get_logger(__name__)


class AgentStateStore:
    """Store for agent state persistence using database."""

    def __init__(self):
        """Initialize state store."""
        # Database-backed persistence for production
        pass

    async def save(self, db: AsyncSession, agent_id: str, state: dict) -> bool:
        """Save agent state to database."""
        logger.info("Saving agent state", agent_id=agent_id)

        try:
            # Check if agent run exists
            result = await db.execute(
                select(AgentRun).where(AgentRun.id == agent_id)
            )
            agent_run = result.scalar_one_or_none()

            if agent_run:
                # Update existing run
                agent_run.status = state.get("status", AgentRunStatus.RUNNING)
                agent_run.current_step_index = state.get("current_step", 0)
                agent_run.cost_used_usd = state.get("budget_remaining", 1.0)

                if state.get("status") in [AgentRunStatus.COMPLETED, AgentRunStatus.ERROR, AgentRunStatus.CANCELLED]:
                    agent_run.completed_at = datetime.utcnow()
                    agent_run.result_summary = str(state.get("final_state", {}))
                    if state.get("status") == AgentRunStatus.ERROR:
                        agent_run.error_reason = "Execution error"
            else:
                # Create new agent run
                agent_run = AgentRun(
                    id=agent_id,
                    agent_type="base_agent",
                    user_id=state.get("user_id"),
                    goal=state.get("goal"),
                    status=state.get("status", AgentRunStatus.RUNNING),
                    current_step_index=state.get("current_step", 0),
                    budget_max_steps=state.get("max_steps", 100),
                    budget_max_cost_usd=1.0,
                    cost_used_usd=state.get("budget_remaining", 1.0),
                    started_at=datetime.utcnow()
                )
                db.add(agent_run)

            # Save steps if present
            steps = state.get("steps", [])
            for step_data in steps:
                step = AgentRunStep(
                    id=f"{agent_id}-step-{step_data['step']}",
                    agent_run_id=agent_id,
                    step_index=step_data["step"],
                    step_type="act",
                    content=str(step_data.get("action", {})),
                    cost_usd=0.0
                )
                db.add(step)

            await db.commit()
            logger.info("Agent state saved", agent_id=agent_id)
            return True

        except Exception as e:
            logger.error("Failed to save agent state", agent_id=agent_id, error=str(e))
            await db.rollback()
            return False

    async def load(self, db: AsyncSession, agent_id: str) -> dict | None:
        """Load agent state from database."""
        try:
            result = await db.execute(
                select(AgentRun).where(AgentRun.id == agent_id)
            )
            agent_run = result.scalar_one_or_none()

            if not agent_run:
                return None

            # Load steps
            steps_result = await db.execute(
                select(AgentRunStep).where(AgentRunStep.agent_run_id == agent_id)
            )
            steps = steps_result.scalars().all()

            state = {
                "agent_id": agent_run.id,
                "user_id": agent_run.user_id,
                "goal": agent_run.goal,
                "status": agent_run.status,
                "current_step": agent_run.current_step_index,
                "budget_remaining": agent_run.budget_max_cost_usd - agent_run.cost_used_usd,
                "max_steps": agent_run.budget_max_steps,
                "steps": [
                    {
                        "step": step.step_index,
                        "action": step.content,
                        "result": step.tool_result,
                        "timestamp": step.created_at.isoformat()
                    }
                    for step in steps
                ],
                "created_at": agent_run.started_at.isoformat(),
                "completed_at": agent_run.completed_at.isoformat() if agent_run.completed_at else None
            }

            return state

        except Exception as e:
            logger.error("Failed to load agent state", agent_id=agent_id, error=str(e))
            return None

    async def delete(self, db: AsyncSession, agent_id: str) -> bool:
        """Delete agent state from database."""
        try:
            result = await db.execute(
                select(AgentRun).where(AgentRun.id == agent_id)
            )
            agent_run = result.scalar_one_or_none()

            if agent_run:
                await db.delete(agent_run)
                await db.commit()
                logger.info("Agent state deleted", agent_id=agent_id)
                return True

            return False

        except Exception as e:
            logger.error("Failed to delete agent state", agent_id=agent_id, error=str(e))
            await db.rollback()
            return False

    async def list_agents(self, db: AsyncSession, user_id: str) -> list:
        """List all agents for user."""
        try:
            result = await db.execute(
                select(AgentRun).where(AgentRun.user_id == user_id)
            )
            agent_runs = result.scalars().all()

            return [
                {
                    "agent_id": run.id,
                    "agent_type": run.agent_type,
                    "goal": run.goal,
                    "status": run.status,
                    "started_at": run.started_at.isoformat(),
                    "completed_at": run.completed_at.isoformat() if run.completed_at else None
                }
                for run in agent_runs
            ]

        except Exception as e:
            logger.error("Failed to list agents", user_id=user_id, error=str(e))
            return []
