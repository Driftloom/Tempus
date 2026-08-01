"""Multi-agent orchestration for complex tasks."""

from enum import Enum
from typing import Any

import structlog

from app.llm.router import llm_router

logger = structlog.get_logger(__name__)


class AgentRole(Enum):
    """Agent roles."""
    PLANNER = "planner"
    RESEARCHER = "researcher"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"
    COORDINATOR = "coordinator"


class Agent:
    """Individual agent with specific role."""

    def __init__(self, role: AgentRole, name: str):
        """Initialize agent."""
        self.role = role
        self.name = name

    async def execute(self, task: str, context: dict[str, Any]) -> dict[str, Any]:
        """Execute agent task."""
        logger.info("Agent executing", agent=self.name, role=self.role.value, task=task)

        messages = self._build_messages(task, context)
        response = await llm_router.complete(messages)

        result = {
            "agent": self.name,
            "role": self.role.value,
            "task": task,
            "result": response.get("choices", [{}])[0].get("message", {}).get("content", ""),
            "tokens_used": response.get("usage", {}).get("total_tokens", 0),
        }

        logger.info("Agent completed", agent=self.name, tokens=result["tokens_used"])
        return result

    def _build_messages(self, task: str, context: dict[str, Any]) -> list[dict[str, str]]:
        """Build messages for LLM."""
        system_message = self._get_system_message()
        user_message = self._build_user_message(task, context)

        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

    def _get_system_message(self) -> str:
        """Get system message for agent role."""
        system_messages = {
            AgentRole.PLANNER: "You are a planning agent. Break down complex tasks into steps.",
            AgentRole.RESEARCHER: "You are a research agent. Gather and analyze information.",
            AgentRole.EXECUTOR: "You are an execution agent. Complete specific tasks.",
            AgentRole.REVIEWER: "You are a review agent. Evaluate and provide feedback.",
            AgentRole.COORDINATOR: "You are a coordinator agent. Manage and orchestrate other agents.",
        }
        return system_messages.get(self.role, "You are a helpful assistant.")

    def _build_user_message(self, task: str, context: dict[str, Any]) -> str:
        """Build user message with context."""
        context_str = "\n".join(f"{k}: {v}" for k, v in context.items())
        return f"Task: {task}\n\nContext:\n{context_str}"


class MultiAgentOrchestrator:
    """Orchestrate multiple agents for complex tasks."""

    def __init__(self):
        """Initialize orchestrator."""
        self.agents = {
            AgentRole.PLANNER: Agent(AgentRole.PLANNER, "Planner"),
            AgentRole.RESEARCHER: Agent(AgentRole.RESEARCHER, "Researcher"),
            AgentRole.EXECUTOR: Agent(AgentRole.EXECUTOR, "Executor"),
            AgentRole.REVIEWER: Agent(AgentRole.REVIEWER, "Reviewer"),
            AgentRole.COORDINATOR: Agent(AgentRole.COORDINATOR, "Coordinator"),
        }

    async def execute_workflow(
        self,
        goal: str,
        context: dict[str, Any],
        workflow: str = "sequential"
    ) -> dict[str, Any]:
        """Execute multi-agent workflow."""
        logger.info("Starting multi-agent workflow", goal=goal, workflow=workflow)

        if workflow == "sequential":
            return await self._sequential_workflow(goal, context)
        elif workflow == "hierarchical":
            return await self._hierarchical_workflow(goal, context)
        else:
            return await self._collaborative_workflow(goal, context)

    async def _sequential_workflow(self, goal: str, context: dict[str, Any]) -> dict[str, Any]:
        """Execute sequential workflow: plan -> research -> execute -> review."""
        results = []

        # Step 1: Plan
        planner_result = await self.agents[AgentRole.PLANNER].execute(
            f"Create a plan for: {goal}",
            context
        )
        results.append(planner_result)

        # Step 2: Research
        researcher_result = await self.agents[AgentRole.RESEARCHER].execute(
            f"Research information for: {goal}",
            {**context, "plan": planner_result["result"]}
        )
        results.append(researcher_result)

        # Step 3: Execute
        executor_result = await self.agents[AgentRole.EXECUTOR].execute(
            f"Execute the plan for: {goal}",
            {**context, "plan": planner_result["result"], "research": researcher_result["result"]}
        )
        results.append(executor_result)

        # Step 4: Review
        reviewer_result = await self.agents[AgentRole.REVIEWER].execute(
            f"Review the execution for: {goal}",
            {**context, "execution": executor_result["result"]}
        )
        results.append(reviewer_result)

        total_tokens = sum(r["tokens_used"] for r in results)

        return {
            "goal": goal,
            "workflow": "sequential",
            "results": results,
            "total_tokens": total_tokens,
            "final_result": reviewer_result["result"],
        }

    async def _hierarchical_workflow(self, goal: str, context: dict[str, Any]) -> dict[str, Any]:
        """Execute hierarchical workflow with coordinator."""
        results = []

        # Coordinator creates sub-tasks
        coordinator_result = await self.agents[AgentRole.COORDINATOR].execute(
            f"Break down {goal} into sub-tasks and assign to appropriate agents",
            context
        )
        results.append(coordinator_result)

        # Execute sub-tasks (simplified)
        executor_result = await self.agents[AgentRole.EXECUTOR].execute(
            f"Execute sub-tasks for: {goal}",
            {**context, "coordination": coordinator_result["result"]}
        )
        results.append(executor_result)

        total_tokens = sum(r["tokens_used"] for r in results)

        return {
            "goal": goal,
            "workflow": "hierarchical",
            "results": results,
            "total_tokens": total_tokens,
            "final_result": executor_result["result"],
        }

    async def _collaborative_workflow(self, goal: str, context: dict[str, Any]) -> dict[str, Any]:
        """Execute collaborative workflow where agents work together."""
        results = []

        # Initial planning
        planner_result = await self.agents[AgentRole.PLANNER].execute(
            f"Initial plan for: {goal}",
            context
        )
        results.append(planner_result)

        # Research and execution in parallel (simplified)
        researcher_result = await self.agents[AgentRole.RESEARCHER].execute(
            f"Research for: {goal}",
            {**context, "plan": planner_result["result"]}
        )
        results.append(researcher_result)

        executor_result = await self.agents[AgentRole.EXECUTOR].execute(
            f"Execute for: {goal}",
            {**context, "plan": planner_result["result"], "research": researcher_result["result"]}
        )
        results.append(executor_result)

        total_tokens = sum(r["tokens_used"] for r in results)

        return {
            "goal": goal,
            "workflow": "collaborative",
            "results": results,
            "total_tokens": total_tokens,
            "final_result": executor_result["result"],
        }


# Global multi-agent orchestrator
multi_agent_orchestrator = MultiAgentOrchestrator()
