"""Base agent class."""

from datetime import datetime
from enum import Enum

from structlog import get_logger

logger = get_logger(__name__)


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    PLANNING = "planning"
    ACTING = "acting"
    OBSERVING = "observing"
    REFLECTING = "reflecting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentBase:
    """Base class for all agents."""

    def __init__(self, agent_id: str, user_id: str, goal: str):
        """Initialize agent."""
        self.agent_id = agent_id
        self.user_id = user_id
        self.goal = goal
        self.status = AgentStatus.IDLE
        self.state = {}
        self.steps = []
        self.current_step = 0
        self.created_at = datetime.utcnow()
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None
        self.budget_remaining = 1.0  # Budget in USD
        self.max_steps = 100

    async def execute(self) -> dict:
        """Execute the agent loop."""
        logger.info("Starting agent execution", agent_id=self.agent_id, goal=self.goal)
        self.status = AgentStatus.PLANNING
        self.started_at = datetime.utcnow()

        try:
            # Plan
            plan = await self.plan()
            logger.info("Plan generated", agent_id=self.agent_id, plan=plan)

            # Execute loop
            result = await self._execute_loop(plan)

            self.status = AgentStatus.COMPLETED
            self.completed_at = datetime.utcnow()
            logger.info("Agent completed", agent_id=self.agent_id)

            return result
        except Exception as e:
            self.status = AgentStatus.FAILED
            logger.error("Agent failed", agent_id=self.agent_id, error=str(e))
            raise

    async def plan(self) -> dict:
        """Generate execution plan."""
        # Override in subclass
        return {"steps": []}

    async def _execute_loop(self, plan: dict) -> dict:
        """Execute plan-act-observe-reflect loop."""
        for step in plan.get("steps", []):
            if self.current_step >= self.max_steps:
                logger.warning("Max steps reached", agent_id=self.agent_id)
                break

            if self.budget_remaining <= 0:
                logger.warning("Budget exhausted", agent_id=self.agent_id)
                break

            # Act
            self.status = AgentStatus.ACTING
            action_result = await self.act(step)
            self.steps.append({
                "step": self.current_step,
                "action": step,
                "result": action_result,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Observe
            self.status = AgentStatus.OBSERVING
            observation = await self.observe(action_result)

            # Reflect
            self.status = AgentStatus.REFLECTING
            reflection = await self.reflect(observation)

            self.current_step += 1

        return {"steps": self.steps, "final_state": self.state}

    async def act(self, step: dict) -> dict:
        """Execute a single action."""
        # Override in subclass
        return {"status": "completed"}

    async def observe(self, action_result: dict) -> dict:
        """Observe the result of an action."""
        # Override in subclass
        return action_result

    async def reflect(self, observation: dict) -> dict:
        """Reflect on observation and update state."""
        # Override in subclass
        return {}

    async def cancel(self) -> bool:
        """Cancel agent execution."""
        self.status = AgentStatus.CANCELLED
        logger.info("Agent cancelled", agent_id=self.agent_id)
        return True

    def get_state(self) -> dict:
        """Get current agent state."""
        return {
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "goal": self.goal,
            "status": self.status.value,
            "state": self.state,
            "steps": self.steps,
            "current_step": self.current_step,
            "budget_remaining": self.budget_remaining,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
