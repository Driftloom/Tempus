"""PII redaction using Microsoft Presidio."""

from enum import Enum

from structlog import get_logger

logger = get_logger(__name__)


class PIICategory(str, Enum):
    """Categories of PII to redact."""
    EMAIL_ADDRESS = "EMAIL_ADDRESS"
    PHONE_NUMBER = "PHONE_NUMBER"
    SSN = "US_SSN"
    CREDIT_CARD = "CREDIT_CARD"
    IP_ADDRESS = "IP_ADDRESS"
    URL = "URL"
    DATE_OF_BIRTH = "DATE_TIME"
    PERSON = "PERSON"
    LOCATION = "LOCATION"
    ORGANIZATION = "ORGANIZATION"
    MEDICAL_LICENSE = "MEDICAL_LICENSE"
    PASSPORT = "PASSPORT"
    DRIVER_LICENSE = "US_DRIVER_LICENSE"


class RedactionMode(str, Enum):
    """Redaction modes."""
    REPLACE = "replace"  # Replace with placeholder
    MASK = "mask"  # Mask with asterisks
    HASH = "hash"  # Replace with hash
    REMOVE = "remove"  # Remove entirely


class PIIEntity:
    """Detected PII entity."""

    def __init__(
        self,
        text: str,
        category: PIICategory,
        start: int,
        end: int,
        confidence: float
    ):
        self.text = text
        self.category = category
        self.start = start
        self.end = end
        self.confidence = confidence


class PIIAnalyzer:
    """Analyzer for detecting PII in text."""

    def __init__(self):
        """Initialize PII analyzer."""
        # In production, would initialize Presidio AnalyzerEngine
        # For now, implement basic pattern-based detection
        self.patterns = {
            PIICategory.EMAIL_ADDRESS: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            PIICategory.PHONE_NUMBER: r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            PIICategory.SSN: r'\b\d{3}-\d{2}-\d{4}\b',
            PIICategory.CREDIT_CARD: r'\b(?:\d[ -]*?){13,16}\b',
            PIICategory.IP_ADDRESS: r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            PIICategory.URL: r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w .-]*/?',
        }

    async def analyze(self, text: str) -> list[PIIEntity]:
        """Analyze text for PII entities."""
        import re

        entities = []

        for category, pattern in self.patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity = PIIEntity(
                    text=match.group(),
                    category=category,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.85  # Pattern-based confidence
                )
                entities.append(entity)

        logger.info("PII analysis complete", entity_count=len(entities))
        return entities


class PIIRedactor:
    """Redactor for PII entities."""

    def __init__(self, mode: RedactionMode = RedactionMode.REPLACE):
        """Initialize PII redactor."""
        self.mode = mode
        self.analyzer = PIIAnalyzer()

    async def redact(
        self,
        text: str,
        categories: list[PIICategory] | None = None,
        mode: RedactionMode | None = None
    ) -> dict:
        """Redact PII from text."""
        mode = mode or self.mode
        categories = categories or list(PIICategory)

        # Analyze for PII
        entities = await self.analyzer.analyze(text)

        # Filter by categories
        filtered_entities = [
            entity for entity in entities
            if entity.category in categories
        ]

        if not filtered_entities:
            return {
                "redacted_text": text,
                "entities": [],
                "redaction_count": 0
            }

        # Sort entities by position (reverse to avoid index shifting)
        filtered_entities.sort(key=lambda e: e.start, reverse=True)

        # Apply redaction
        redacted_text = text
        for entity in filtered_entities:
            redacted_text = self._apply_redaction(
                redacted_text,
                entity,
                mode
            )

        logger.info(
            "PII redaction complete",
            entity_count=len(filtered_entities),
            mode=mode
        )

        return {
            "redacted_text": redacted_text,
            "entities": [
                {
                    "category": entity.category.value,
                    "text": entity.text,
                    "start": entity.start,
                    "end": entity.end,
                    "confidence": entity.confidence
                }
                for entity in filtered_entities
            ],
            "redaction_count": len(filtered_entities)
        }

    def _apply_redaction(
        self,
        text: str,
        entity: PIIEntity,
        mode: RedactionMode
    ) -> str:
        """Apply redaction to a single entity."""
        placeholder = f"[{entity.category.value}]"

        if mode == RedactionMode.REPLACE:
            return text[:entity.start] + placeholder + text[entity.end:]

        elif mode == RedactionMode.MASK:
            masked = "*" * len(entity.text)
            return text[:entity.start] + masked + text[entity.end:]

        elif mode == RedactionMode.HASH:
            import hashlib
            hashed = hashlib.sha256(entity.text.encode()).hexdigest()[:8]
            return text[:entity.start] + f"[HASH:{hashed}]" + text[entity.end:]

        elif mode == RedactionMode.REMOVE:
            return text[:entity.start] + text[entity.end:]

        return text

    async def redact_for_llm(
        self,
        text: str,
        provenance: str | None = None
    ) -> str:
        """Redact PII specifically for LLM context."""
        # Use stricter redaction for untrusted sources
        if provenance and "untrusted" in provenance:
            result = await self.redact(
                text,
                mode=RedactionMode.REPLACE
            )
        else:
            result = await self.redact(
                text,
                categories=[
                    PIICategory.SSN,
                    PIICategory.CREDIT_CARD,
                    PIICategory.PHONE_NUMBER,
                    PIICategory.EMAIL_ADDRESS
                ],
                mode=RedactionMode.MASK
            )

        return result["redacted_text"]


class PIIPolicyEnforcer:
    """Enforcer for PII policies based on provenance."""

    def __init__(self):
        """Initialize PII policy enforcer."""
        self.redactor = PIIRedactor()
        self.policies = {
            "external_untrusted:email": {
                "redact_all": True,
                "mode": RedactionMode.REPLACE,
                "categories": list(PIICategory)
            },
            "external_untrusted:web": {
                "redact_all": True,
                "mode": RedactionMode.REPLACE,
                "categories": list(PIICategory)
            },
            "external_untrusted:connector": {
                "redact_all": True,
                "mode": RedactionMode.REPLACE,
                "categories": list(PIICategory)
            },
            "user_direct": {
                "redact_all": False,
                "mode": RedactionMode.MASK,
                "categories": [PIICategory.SSN, PIICategory.CREDIT_CARD]
            },
            "internal_memory": {
                "redact_all": False,
                "mode": RedactionMode.MASK,
                "categories:": [PIICategory.SSN, PIICategory.CREDIT_CARD]
            }
        }

    async def enforce_policy(
        self,
        text: str,
        provenance: str
    ) -> dict:
        """Enforce PII policy based on provenance."""
        policy = self.policies.get(provenance, self.policies["user_direct"])

        if not policy["redact_all"]:
            # Only redact sensitive categories
            result = await self.redactor.redact(
                text,
                categories=policy["categories"],
                mode=policy["mode"]
            )
        else:
            # Redact all PII
            result = await self.redactor.redact(
                text,
                categories=policy["categories"],
                mode=policy["mode"]
            )

        return {
            "redacted_text": result["redacted_text"],
            "provenance": provenance,
            "policy": policy,
            "entities_detected": result["redaction_count"]
        }
