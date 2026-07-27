"""Middleware for applying guardrails to LLM requests."""

from typing import Dict, Optional
from app.guardrails.validator import GuardrailValidator, GuardrailViolation, ViolationSeverity
from app.guardrails.filter import ContentFilter
from structlog import get_logger

logger = get_logger(__name__)


class GuardrailMiddleware:
    """Middleware for applying guardrails."""
    
    def __init__(self, validator: GuardrailValidator, filter: ContentFilter):
        """Initialize guardrail middleware."""
        self.validator = validator
        self.filter = filter
        self.strict_mode = False
    
    async def process_request(
        self,
        input_text: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """Process request through guardrails."""
        logger.info("Processing request through guardrails")
        
        # Validate input
        input_violations = await self.validator.validate_input(input_text, context)
        
        if input_violations:
            # Check for critical violations
            critical_violations = [v for v in input_violations if v.severity == ViolationSeverity.CRITICAL]
            
            if critical_violations or self.strict_mode:
                logger.warning("Request blocked by guardrails", violations=len(input_violations))
                return {
                    "allowed": False,
                    "reason": "guardrail_violation",
                    "violations": [v.__dict__ for v in input_violations]
                }
        
        return {
            "allowed": True,
            "violations": [v.__dict__ for v in input_violations]
        }
    
    async def process_response(
        self,
        output_text: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """Process response through guardrails."""
        logger.info("Processing response through guardrails")
        
        # Validate output
        output_violations = await self.validator.validate_output(output_text, context)
        
        # Filter output
        filtered = await self.filter.filter_output(output_text, context)
        
        if output_violations:
            # Check for critical violations
            critical_violations = [v for v in output_violations if v.severity == ViolationSeverity.CRITICAL]
            
            if critical_violations or self.strict_mode:
                logger.warning("Response blocked by guardrails", violations=len(output_violations))
                return {
                    "allowed": False,
                    "reason": "guardrail_violation",
                    "violations": [v.__dict__ for v in output_violations]
                }
        
        return {
            "allowed": True,
            "filtered_output": filtered["filtered_output"],
            "was_filtered": filtered["was_filtered"],
            "filter_actions": filtered["actions"],
            "violations": [v.__dict__ for v in output_violations]
        }
    
    def set_strict_mode(self, strict: bool):
        """Set strict mode."""
        self.strict_mode = strict
        logger.info("Strict mode changed", strict=strict)
