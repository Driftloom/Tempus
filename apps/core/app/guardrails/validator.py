"""Input/output validation for LLM interactions."""

from enum import Enum

from structlog import get_logger

logger = get_logger(__name__)


class ViolationSeverity(str, Enum):
    """Severity of guardrail violation."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GuardrailViolation:
    """Guardrail violation."""

    def __init__(
        self,
        rule_id: str,
        severity: ViolationSeverity,
        message: str,
        details: dict | None = None
    ):
        """Initialize violation."""
        self.rule_id = rule_id
        self.severity = severity
        self.message = message
        self.details = details or {}


class GuardrailValidator:
    """Validator for LLM inputs and outputs."""

    def __init__(self):
        """Initialize guardrail validator."""
        self.rules = {
            "no_pii": self._check_pii,
            "no_harmful_content": self._check_harmful_content,
            "no_code_execution": self._check_code_execution,
            "max_length": self._check_max_length,
            "no_sensitive_data": self._check_sensitive_data
        }
        self.max_input_length = 10000
        self.max_output_length = 20000

    async def validate_input(self, input_text: str, context: dict | None = None) -> list[GuardrailViolation]:
        """Validate input against guardrails."""
        violations = []

        for rule_id, rule_func in self.rules.items():
            try:
                violation = await rule_func(input_text, context)
                if violation:
                    violations.append(violation)
            except Exception as e:
                logger.error("Guardrule check failed", rule_id=rule_id, error=str(e))

        return violations

    async def validate_output(self, output_text: str, context: dict | None = None) -> list[GuardrailViolation]:
        """Validate output against guardrails."""
        violations = []

        # Check output-specific rules
        if len(output_text) > self.max_output_length:
            violations.append(GuardrailViolation(
                rule_id="max_output_length",
                severity=ViolationSeverity.MEDIUM,
                message=f"Output exceeds maximum length of {self.max_output_length}",
                details={"length": len(output_text)}
            ))

        # Run general rules
        for rule_id, rule_func in self.rules.items():
            if rule_id != "max_length":  # Skip input-specific rule
                try:
                    violation = await rule_func(output_text, context)
                    if violation:
                        violations.append(violation)
                except Exception as e:
                    logger.error("Guardrule check failed", rule_id=rule_id, error=str(e))

        return violations

    async def _check_pii(self, text: str, context: dict | None) -> GuardrailViolation | None:
        """Check for personally identifiable information."""
        pii_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"\b\d{16}\b",  # Credit card
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"  # Email
        ]

        import re
        for pattern in pii_patterns:
            if re.search(pattern, text):
                return GuardrailViolation(
                    rule_id="no_pii",
                    severity=ViolationSeverity.HIGH,
                    message="Text contains potentially sensitive PII",
                    details={"pattern": pattern}
                )

        return None

    async def _check_harmful_content(self, text: str, context: dict | None) -> GuardrailViolation | None:
        """Check for harmful content."""
        harmful_keywords = [
            "hack", "exploit", "malware", "virus", "attack",
            "illegal", "fraud", "scam"
        ]

        text_lower = text.lower()
        for keyword in harmful_keywords:
            if keyword in text_lower:
                return GuardrailViolation(
                    rule_id="no_harmful_content",
                    severity=ViolationSeverity.HIGH,
                    message=f"Text contains potentially harmful keyword: {keyword}",
                    details={"keyword": keyword}
                )

        return None

    async def _check_code_execution(self, text: str, context: dict | None) -> GuardrailViolation | None:
        """Check for code execution attempts."""
        code_keywords = [
            "exec(", "eval(", "__import__", "subprocess",
            "os.system", "pickle.loads"
        ]

        for keyword in code_keywords:
            if keyword in text:
                return GuardrailViolation(
                    rule_id="no_code_execution",
                    severity=ViolationSeverity.CRITICAL,
                    message=f"Text contains code execution keyword: {keyword}",
                    details={"keyword": keyword}
                )

        return None

    async def _check_max_length(self, text: str, context: dict | None) -> GuardrailViolation | None:
        """Check maximum length."""
        if len(text) > self.max_input_length:
            return GuardrailViolation(
                rule_id="max_length",
                severity=ViolationSeverity.MEDIUM,
                message=f"Input exceeds maximum length of {self.max_input_length}",
                details={"length": len(text)}
            )
        return None

    async def _check_sensitive_data(self, text: str, context: dict | None) -> GuardrailViolation | None:
        """Check for sensitive data."""
        sensitive_keywords = [
            "password", "api_key", "secret", "token",
            "private_key", "credential"
        ]

        text_lower = text.lower()
        for keyword in sensitive_keywords:
            if keyword in text_lower:
                return GuardrailViolation(
                    rule_id="no_sensitive_data",
                    severity=ViolationSeverity.HIGH,
                    message=f"Text contains sensitive keyword: {keyword}",
                    details={"keyword": keyword}
                )

        return None
