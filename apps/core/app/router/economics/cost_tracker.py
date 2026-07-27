"""Cost tracker for LLM usage."""

from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import AsyncSessionLocal
from structlog import get_logger

logger = get_logger(__name__)


class CostTracker:
    """Tracker for LLM usage costs."""
    
    def __init__(self):
        """Initialize cost tracker."""
        self.costs = {}  # In-memory tracking (would use database in production)
        self.daily_budget = 1.0  # $1 per day default
        self.daily_spent = 0.0
    
    async def track(
        self,
        user_id: Optional[str],
        provider: str,
        model: str,
        cost: float
    ) -> None:
        """Track LLM usage cost."""
        logger.info("Tracking cost", user_id=user_id, provider=provider, model=model, cost=cost)
        
        # Update daily spent
        self.daily_spent += cost
        
        # Check budget
        if self.daily_spent > self.daily_budget:
            logger.warning("Daily budget exceeded", spent=self.daily_spent, budget=self.daily_budget)
        
        # Store cost record
        if user_id not in self.costs:
            self.costs[user_id] = []
        
        self.costs[user_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "provider": provider,
            "model": model,
            "cost": cost
        })
    
    def get_daily_spent(self) -> float:
        """Get total daily spending."""
        return self.daily_spent
    
    def get_user_costs(self, user_id: str) -> list:
        """Get costs for specific user."""
        return self.costs.get(user_id, [])
    
    def check_budget(self, estimated_cost: float) -> bool:
        """Check if estimated cost fits within budget."""
        return (self.daily_spent + estimated_cost) <= self.daily_budget
    
    def reset_daily(self) -> None:
        """Reset daily tracking (called at midnight)."""
        self.daily_spent = 0.0
        self.costs = {}
        logger.info("Daily costs reset")
