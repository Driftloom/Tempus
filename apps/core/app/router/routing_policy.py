"""Routing policy for sensitivity-based LLM routing."""


from structlog import get_logger

logger = get_logger(__name__)


class RoutingPolicy:
    """Policy for routing requests to local or cloud LLMs."""

    def __init__(self) -> None:
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

    def classify_sensitivity(self, prompt: str, context: dict | None = None) -> str:
        """Classify content sensitivity based on keywords and context.
        
        Args:
            prompt: The input prompt to classify
            context: Optional context dictionary with sensitivity information
            
        Returns:
            Sensitivity level: "high", "medium", or "low"
        """
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

    def classify_complexity(self, prompt: str, context: dict | None = None) -> str:
        """Classify request complexity based on keywords and length.
        
        Args:
            prompt: The input prompt to classify
            context: Optional context dictionary
            
        Returns:
            Complexity level: "high", "medium", or "low"
        """
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

    def decide(self, sensitivity: str, complexity: str) -> dict:
        """Make routing decision based on sensitivity and complexity.
        
        Args:
            sensitivity: Sensitivity level ("high", "medium", "low")
            complexity: Complexity level ("high", "medium", "low")
            
        Returns:
            Dictionary with provider, model, and reason for the decision
        """
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
