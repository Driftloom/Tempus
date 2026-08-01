"""Sensitivity classifier for memory items."""

from structlog import get_logger

from app.database.models.memory import MemorySensitivity

logger = get_logger(__name__)


class SensitivityClassifier:
    """Classifier for determining memory sensitivity."""

    # High sensitivity keywords
    HIGH_SENSITIVITY_KEYWORDS = [
        "password", "ssn", "social security", "credit card", "bank account",
        "health", "medical", "diagnosis", "prescription", "doctor",
        "salary", "income", "financial", "tax", "secret", "private",
        "confidential", "personal", "address", "phone number"
    ]

    # Medium sensitivity keywords
    MEDIUM_SENSITIVITY_KEYWORDS = [
        "work", "project", "client", "meeting", "schedule",
        "deadline", "task", "assignment", "professional"
    ]

    def classify(self, content: str, source: str) -> MemorySensitivity:
        """Classify content sensitivity level."""
        content_lower = content.lower()

        # Check for high sensitivity
        if self._contains_keywords(content_lower, self.HIGH_SENSITIVITY_KEYWORDS):
            return MemorySensitivity.HIGH

        # Check for medium sensitivity
        if self._contains_keywords(content_lower, self.MEDIUM_SENSITIVITY_KEYWORDS):
            return MemorySensitivity.MEDIUM

        # External sources default to medium
        if source in ["email", "external"]:
            return MemorySensitivity.MEDIUM

        # Default to low
        return MemorySensitivity.LOW

    def _contains_keywords(self, content: str, keywords: List[str]) -> bool:
        """Check if content contains any of the keywords."""
        return any(keyword in content for keyword in keywords)
