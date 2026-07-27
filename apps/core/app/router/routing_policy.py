"""Routing policy for sensitivity-based LLM routing."""

from typing import Dict, Optional
from structlog import get_logger

logger = get_logger(__name__)


class RoutingPolicy:
    """Policy for routing requests to local or cloud LLMs."""
    
    def __init__(self):
        """Initialize routing policy."""
        # High sensitivity keywords
        self.high_sensitivity_keywords = [
            "password", "ssn", "credit card", "health", "medical",
            "salary", "financial", "personal", "private", "confidential"
        ]
        
        # High complexity indicators
        self.high_complexity_keywords = [
            "analyze", "synthesize", "compare", "evaluate", "reason",
            "complex", "detailed", "comprehensive", "strategic"
        ]
    
    def classify_sensitivity(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Classify content sensitivity."""
        prompt_lower = prompt.lower()
        
        # Check for high sensitivity keywords
        for keyword in self.high_sensitivity_keywords:
            if keyword in prompt_lower:
                return "high"
        
        # Check context for sensitivity
        if context and context.get("sensitivity") == "high":
            return "high"
        
        # Default to medium
        return "medium"
    
    def classify_complexity(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Classify request complexity."""
        prompt_lower = prompt.lower()
        
        # Check for high complexity keywords
        for keyword in self.high_complexity_keywords:
            if keyword in prompt_lower:
                return "high"
        
        # Check prompt length
        if len(prompt) > 500:
            return "high"
        
        # Default to low
        return "low"
    
    def decide(self, sensitivity: str, complexity: str) -> Dict:
        """Make routing decision based on sensitivity and complexity."""
        # High sensitivity always goes local
        if sensitivity == "high":
            return {
                "provider": "local",
                "model": "llama2",
                "reason": "high_sensitivity"
            }
        
        # High complexity with low/medium sensitivity goes cloud
        if complexity == "high" and sensitivity in ["low", "medium"]:
            return {
                "provider": "cloud",
                "model": "claude-3-sonnet",
                "reason": "high_complexity_low_sensitivity"
            }
        
        # Low complexity with low/medium sensitivity goes local
        if complexity == "low":
            return {
                "provider": "local",
                "model": "llama2",
                "reason": "low_complexity"
            }
        
        # Default to local for medium complexity
        return {
            "provider": "local",
            "model": "llama2",
            "reason": "default"
        }
