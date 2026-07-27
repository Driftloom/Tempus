"""Supervisor for multi-agent orchestration."""

from typing import Dict, List, Optional
from app.agents.runtime.agent_base import AgentBase
from app.agents.loop.loop_engine import LoopEngine
from structlog import get_logger

logger = get_logger(__name__)


class Supervisor:
    """Supervisor for orchestrating multiple agents."""
    
    def __init__(self, loop_engine: LoopEngine):
        """Initialize supervisor."""
        self.loop_engine = loop_engine
        self.agent_registry = {}
        self.active_orchestrations = {}
    
    def register_agent_type(self, agent_type: str, agent_class: type):
        """Register an agent type."""
        logger.info("Registering agent type", agent_type=agent_type)
        self.agent_registry[agent_type] = agent_class
    
    async def orchestrate(
        self,
        user_id: str,
        goal: str,
        agent_types: List[str]
    ) -> Dict:
        """Orchestrate multiple agents to complete a goal."""
        logger.info("Orchestrating agents", user_id=user_id, goal=goal, agent_types=agent_types)
        
        orchestration_id = f"orch-{user_id}-{hash(goal)}"
        
        # Create agents
        agents = []
        for agent_type in agent_types:
            if agent_type not in self.agent_registry:
                logger.warning("Agent type not registered", agent_type=agent_type)
                continue
            
            agent_id = f"{agent_type}-{orchestration_id}"
            agent_class = self.agent_registry[agent_type]
            agent = agent_class(agent_id, user_id, goal)
            agents.append(agent)
        
        # Execute agents
        results = await self._execute_agents(agents)
        
        # Merge results
        merged_result = self._merge_results(results)
        
        self.active_orchestrations[orchestration_id] = {
            "agents": [a.agent_id for a in agents],
            "results": results,
            "merged_result": merged_result
        }
        
        logger.info("Orchestration completed", orchestration_id=orchestration_id)
        return merged_result
    
    async def _execute_agents(self, agents: List[AgentBase]) -> List[Dict]:
        """Execute agents concurrently or sequentially."""
        results = []
        
        for agent in agents:
            try:
                result = await self.loop_engine.start_agent(agent)
                results.append({
                    "agent_id": agent.agent_id,
                    "status": "completed",
                    "result": result
                })
            except Exception as e:
                logger.error("Agent execution failed", agent_id=agent.agent_id, error=str(e))
                results.append({
                    "agent_id": agent.agent_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        return results
    
    def _merge_results(self, results: List[Dict]) -> Dict:
        """Merge results from multiple agents."""
        merged = {
            "total_agents": len(results),
            "successful": sum(1 for r in results if r["status"] == "completed"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "agent_results": results
        }
        return merged
    
    async def cancel_orchestration(self, orchestration_id: str) -> bool:
        """Cancel an active orchestration."""
        if orchestration_id not in self.active_orchestrations:
            return False
        
        orchestration = self.active_orchestrations[orchestration_id]
        
        # Cancel all agents
        for agent_id in orchestration["agents"]:
            await self.loop_engine.cancel_agent(agent_id)
        
        del self.active_orchestrations[orchestration_id]
        logger.info("Orchestration cancelled", orchestration_id=orchestration_id)
        return True
    
    def list_agent_types(self) -> List[str]:
        """List registered agent types."""
        return list(self.agent_registry.keys())
