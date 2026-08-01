"""Content filtering for LLM outputs."""


from structlog import get_logger

logger = get_logger(__name__)


class ContentFilter:
    """Filter for LLM output content."""

    def __init__(self):
        """Initialize content filter."""
        self.blocked_domains = []
        self.blocked_patterns = []

    async def filter_output(self, output: str, context: dict | None = None) -> dict:
        """Filter output content."""
        filtered_output = output
        filter_actions = []

        # Remove blocked domains
        for domain in self.blocked_domains:
            if domain in filtered_output:
                filtered_output = filtered_output.replace(domain, "[REDACTED]")
                filter_actions.append({
                    "action": "redact",
                    "reason": "blocked_domain",
                    "value": domain
                })

        # Remove blocked patterns
        for pattern in self.blocked_patterns:
            import re
            matches = re.findall(pattern, filtered_output)
            if matches:
                for match in matches:
                    filtered_output = filtered_output.replace(match, "[REDACTED]")
                    filter_actions.append({
                        "action": "redact",
                        "reason": "blocked_pattern",
                        "value": match
                    })

        return {
            "filtered_output": filtered_output,
            "actions": filter_actions,
            "was_filtered": len(filter_actions) > 0
        }

    def add_blocked_domain(self, domain: str):
        """Add a blocked domain."""
        self.blocked_domains.append(domain)
        logger.info("Blocked domain added", domain=domain)

    def add_blocked_pattern(self, pattern: str):
        """Add a blocked regex pattern."""
        self.blocked_patterns.append(pattern)
        logger.info("Blocked pattern added", pattern=pattern)
