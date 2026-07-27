"""Loop engine for agent execution."""

from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.runtime.agent_base import AgentBase
from app.agents.runtime.state_store import AgentStateStore
from structlog import get_logger

logger = get_logger(__name__)


class LoopEngine:
    """Engine for managing agent execution loops."""
    
    def __init__(self, state_store: AgentStateStore):
        """Initialize loop engine."""
        self.state_store = state_store
        self.active_agents = {}
    
    async def start_agent(self, db: AsyncSession, agent: AgentBase) -> str:
        """Start an agent execution."""
        logger.info("Starting agent", agent_id=agent.agent_id)
        
        # Save initial state
        await self.state_store.save(db, agent.agent_id, agent.get_state())
        
        # Track active agent
        self.active_agents[agent.agent_id] = agent
        
        # Execute agent
        result = await agent.execute()
        
        # Save final state
        await self.state_store.save(db, agent.agent_id, agent.get_state())
        
        # Remove from active
        del self.active_agents[agent.agent_id]
        
        return result
    
    async def pause_agent(self, db: AsyncSession, agent_id: str) -> bool:
        """Pause an agent execution."""
        if agent_id in self.active_agents:
            agent = self.active_agents[agent_id]
            # Save current state
            await self.state_store.save(db, agent_id, agent.get_state())
            logger.info("Agent paused", agent_id=agent_id)
            return True
        return False
    
    async def resume_agent(self, db: AsyncSession, agent_id: str) -> Optional[Dict]:
        """Resume a paused agent."""
        # Load state
        state = await self.state_store.load(db, agent_id)
        if not state:
            logger.warning("Agent state not found", agent_id=agent_id)
            return None
        
        # Recreate agent from state
        # In production, would reconstruct agent from state
        logger.info("Resuming agent", agent_id=agent_id)
        
        return state
    
    async def cancel_agent(self, db: AsyncSession, agent_id: str) -> bool:
        """Cancel an agent execution."""
        if agent_id in self.active_agents:
            agent = self.active_agents[agent_id]
            await agent.cancel()
            await self.state_store.save(db, agent_id, agent.get_state())
            del self.active_agents[agent_id]
            logger.info("Agent cancelled", agent_id=agent_id)
            return True
        return False
    
    async def get_agent_status(self, db: AsyncSession, agent_id: str) -> Optional[Dict]:
        """Get agent status."""
        state = await self.state_store.load(db, agent_id)
        if state:
            return {
                "agent_id": agent_id,
                "status": state.get("status"),
                "current_step": state.get("current_step"),
                "budget_remaining": state.get("budget_remaining")
            }
        return None
    
    def list_active_agents(self) -> list:
        """List all active agents."""
        return list(self.active_agents.keys())
