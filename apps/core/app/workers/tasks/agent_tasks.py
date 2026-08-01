"""Celery tasks for agent execution."""

import structlog
from celery import shared_task

from app.agents.loop.loop_engine import LoopEngine
from app.database.session import AsyncSessionLocal

logger = structlog.get_logger(__name__)


@shared_task(bind=True, max_retries=3)
def execute_agent(self, agent_id: str, user_id: str, goal: str):
    """Execute an agent in the background."""
    logger.info("Executing agent", agent_id=agent_id, user_id=user_id, goal=goal)

    try:
        async def _execute():
            async with AsyncSessionLocal() as db:
                loop_engine = LoopEngine(db)
                result = await loop_engine.start_agent(agent_id, user_id, goal)
                return result

        import asyncio
        result = asyncio.run(_execute())
        logger.info("Agent executed", agent_id=agent_id, user_id=user_id)
        return {"status": "success", "agent_id": agent_id, "result": result}

    except Exception as e:
        logger.error("Agent execution failed", agent_id=agent_id, user_id=user_id, error=str(e))
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task
def cleanup_agent_runs():
    """Clean up old agent runs."""
    logger.info("Cleaning up old agent runs")

    try:
        async def _cleanup():
            async with AsyncSessionLocal() as db:
                from datetime import datetime, timedelta

                from sqlalchemy import delete

                from app.database.models.agent_runs import AgentRun

                # Delete runs older than 30 days
                cutoff = datetime.utcnow() - timedelta(days=30)
                await db.execute(
                    delete(AgentRun).where(AgentRun.created_at < cutoff)
                )
                await db.commit()

        import asyncio
        asyncio.run(_cleanup())
        logger.info("Old agent runs cleaned up")
        return {"status": "success"}

    except Exception as e:
        logger.error("Agent run cleanup failed", error=str(e))
        raise


@shared_task
def monitor_agent_costs():
    """Monitor and report on agent costs."""
    logger.info("Monitoring agent costs")

    try:
        async def _monitor():
            async with AsyncSessionLocal() as db:
                from datetime import datetime, timedelta

                from sqlalchemy import func, select

                from app.database.models.agent_runs import AgentRun

                # Calculate costs for the last 24 hours
                cutoff = datetime.utcnow() - timedelta(days=1)
                result = await db.execute(
                    select(
                        func.sum(AgentRun.cost_used),
                        func.count(AgentRun.id)
                    ).where(AgentRun.created_at >= cutoff)
                )
                total_cost, count = result.one()

                logger.info("Agent cost report", total_cost=total_cost, count=count)
                return {"total_cost": total_cost, "count": count}

        import asyncio
        result = asyncio.run(_monitor())
        return {"status": "success", **result}

    except Exception as e:
        logger.error("Agent cost monitoring failed", error=str(e))
        raise
