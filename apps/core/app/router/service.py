"""Router service for hybrid LLM routing."""

from typing import Dict, Optional
from app.router.policy.routing_policy import RoutingPolicy
from app.router.gateway.llm_gateway import LLMGateway
from app.router.cache.response_cache import ResponseCache
from app.router.economics.cost_tracker import CostTracker
from structlog import get_logger

logger = get_logger(__name__)


class RouterService:
    """Service for routing LLM requests to appropriate providers."""
    
    def __init__(
        self,
        routing_policy: RoutingPolicy,
        llm_gateway: LLMGateway,
        response_cache: ResponseCache,
        cost_tracker: CostTracker
    ):
        """Initialize router service."""
        self.routing_policy = routing_policy
        self.llm_gateway = llm_gateway
        self.response_cache = response_cache
        self.cost_tracker = cost_tracker
    
    async def route(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        sensitivity: Optional[str] = None,
        complexity: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """Route request to appropriate LLM provider."""
        logger.info("Routing request", sensitivity=sensitivity, complexity=complexity)
        
        # Determine sensitivity if not provided
        if not sensitivity:
            sensitivity = self.routing_policy.classify_sensitivity(prompt, context)
        
        # Determine complexity if not provided
        if not complexity:
            complexity = self.routing_policy.classify_complexity(prompt, context)
        
        # Check cache first
        cache_key = self._generate_cache_key(prompt, sensitivity, complexity)
        cached_response = await self.response_cache.get(cache_key)
        if cached_response:
            logger.info("Cache hit", cache_key=cache_key)
            return cached_response
        
        # Determine routing decision
        routing_decision = self.routing_policy.decide(sensitivity, complexity)
        
        logger.info("Routing decision", decision=routing_decision)
        
        # Execute request via gateway
        response = await self.llm_gateway.execute(
            prompt=prompt,
            provider=routing_decision["provider"],
            model=routing_decision["model"],
            context=context
        )
        
        # Track cost
        await self.cost_tracker.track(
            user_id=user_id,
            provider=routing_decision["provider"],
            model=routing_decision["model"],
            cost=response.get("cost", 0)
        )
        
        # Cache response
        await self.response_cache.set(cache_key, response)
        
        return response
    
    def _generate_cache_key(self, prompt: str, sensitivity: str, complexity: str) -> str:
        """Generate cache key for request."""
        import hashlib
        key_string = f"{prompt}:{sensitivity}:{complexity}"
        return hashlib.md5(key_string.encode()).hexdigest()
