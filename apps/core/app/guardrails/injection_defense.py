"""Prompt injection defense for guardrails layer."""

from typing import Dict, Optional, List
from enum import Enum
from structlog import get_logger

logger = get_logger(__name__)


class InjectionType(str, Enum):
    """Types of prompt injection attacks."""
    DIRECT_INSTRUCTION = "direct_instruction"
    ROLE_PLAYING = "role_playing"
    CONTEXT_MANIPULATION = "context_manipulation"
    CODE_INJECTION = "code_injection"
    DATA_EXFILTRATION = "data_exfiltration"
    JAILBREAK_ATTEMPT = "jailbreak_attempt"


class InjectionSeverity(str, Enum):
    """Severity of injection attempt."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InjectionResult:
    """Result of injection detection."""
    
    def __init__(
        self,
        detected: bool,
        injection_type: Optional[InjectionType],
        severity: Optional[InjectionSeverity],
        confidence: float,
        details: Optional[Dict] = None
    ):
        self.detected = detected
        self.injection_type = injection_type
        self.severity = severity
        self.confidence = confidence
        self.details = details or {}


class InjectionClassifier:
    """Classifier for detecting prompt injection attacks."""
    
    def __init__(self):
        """Initialize injection classifier."""
        self.injection_patterns = {
            InjectionType.DIRECT_INSTRUCTION: [
                "ignore previous instructions",
                "disregard all above",
                "forget everything",
                "new instruction",
                "override",
                "system: ignore",
                "developer mode",
                "admin mode"
            ],
            InjectionType.ROLE_PLAYING: [
                "you are now",
                "act as",
                "pretend to be",
                "roleplay as",
                "simulate",
                "imagine you are",
                "from now on you are"
            ],
            InjectionType.CONTEXT_MANIPULATION: [
                "the real task is",
                "actually i want",
                "change the objective",
                "modify the goal",
                "the user actually meant",
                "reinterpret the request"
            ],
            InjectionType.CODE_INJECTION: [
                "exec(",
                "eval(",
                "__import__",
                "subprocess",
                "os.system",
                "pickle.loads",
                "compile(",
                "globals()",
                "locals()"
            ],
            InjectionType.DATA_EXFILTRATION: [
                "print all",
                "show me your",
                "reveal your",
                "output your",
                "display your",
                "what are your instructions",
                "what is your system prompt"
            ],
            InjectionType.JAILBREAK_ATTEMPT: [
                "dan",
                "jailbreak",
                "bypass restrictions",
                "ignore safety",
                "disable filters",
                "remove constraints",
                "unrestricted mode"
            ]
        }
        
        self.high_risk_sources = [
            "external_untrusted:email",
            "external_untrusted:web",
            "external_untrusted:connector"
        ]
    
    async def classify(
        self,
        text: str,
        context: Optional[Dict] = None
    ) -> InjectionResult:
        """Classify text for injection attempts."""
        context = context or {}
        text_lower = text.lower()
        
        # Check provenance
        provenance = context.get("provenance", "user_direct")
        is_untrusted = provenance in self.high_risk_sources
        
        # Scan for injection patterns
        detected_injections = []
        
        for injection_type, patterns in self.injection_patterns.items():
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    detected_injections.append({
                        "type": injection_type,
                        "pattern": pattern,
                        "match_count": text_lower.count(pattern.lower())
                    })
        
        if not detected_injections:
            return InjectionResult(
                detected=False,
                injection_type=None,
                severity=None,
                confidence=0.0
            )
        
        # Determine severity based on injection type and count
        injection_types = [inj["type"] for inj in detected_injections]
        match_count = sum(inj["match_count"] for inj in detected_injections)
        
        # Critical injections
        if InjectionType.JAILBREAK_ATTEMPT in injection_types or InjectionType.CODE_INJECTION in injection_types:
            severity = InjectionSeverity.CRITICAL
            confidence = min(0.9 + (match_count * 0.05), 1.0)
        # High severity
        elif InjectionType.DIRECT_INSTRUCTION in injection_types or InjectionType.DATA_EXFILTRATION in injection_types:
            severity = InjectionSeverity.HIGH
            confidence = min(0.8 + (match_count * 0.05), 1.0)
        # Medium severity
        elif InjectionType.ROLE_PLAYING in injection_types or InjectionType.CONTEXT_MANIPULATION in injection_types:
            severity = InjectionSeverity.MEDIUM
            confidence = min(0.7 + (match_count * 0.05), 1.0)
        else:
            severity = InjectionSeverity.LOW
            confidence = min(0.6 + (match_count * 0.05), 1.0)
        
        # Boost confidence for untrusted sources
        if is_untrusted:
            confidence = min(confidence + 0.2, 1.0)
            # Upgrade severity for untrusted sources
            if severity == InjectionSeverity.MEDIUM:
                severity = InjectionSeverity.HIGH
            elif severity == InjectionSeverity.LOW:
                severity = InjectionSeverity.MEDIUM
        
        return InjectionResult(
            detected=True,
            injection_type=injection_types[0],  # Primary type
            severity=severity,
            confidence=confidence,
            details={
                "detected_patterns": detected_injections,
                "provenance": provenance,
                "is_untrusted": is_untrusted
            }
        )
    
    def should_block(self, result: InjectionResult, strict_mode: bool = False) -> bool:
        """Determine if content should be blocked based on injection result."""
        if not result.detected:
            return False
        
        # Always block critical injections
        if result.severity == InjectionSeverity.CRITICAL:
            return True
        
        # Block high severity in strict mode or with high confidence
        if result.severity == InjectionSeverity.HIGH:
            return strict_mode or result.confidence > 0.8
        
        # Block medium severity in strict mode with high confidence
        if result.severity == InjectionSeverity.MEDIUM:
            return strict_mode and result.confidence > 0.9
        
        return False


class ProvenanceEnforcer:
    """Enforcer for provenance-based policies."""
    
    def __init__(self):
        """Initialize provenance enforcer."""
        self.policies = {
            "external_untrusted:email": {
                "allowed_in_llm_context": False,
                "requires_user_approval": True,
                "max_context_length": 500,
                "must_be_redacted": True
            },
            "external_untrusted:web": {
                "allowed_in_llm_context": False,
                "requires_user_approval": True,
                "max_context_length": 300,
                "must_be_redacted": True
            },
            "external_untrusted:connector": {
                "allowed_in_llm_context": False,
                "requires_user_approval": True,
                "max_context_length": 1000,
                "must_be_redacted": True
            },
            "user_direct": {
                "allowed_in_llm_context": True,
                "requires_user_approval": False,
                "max_context_length": None,
                "must_be_redacted": False
            },
            "internal_memory": {
                "allowed_in_llm_context": True,
                "requires_user_approval": False,
                "max_context_length": None,
                "must_be_redacted": False
            }
        }
    
    def check_permission(
        self,
        provenance: str,
        action: str = "use_in_llm_context"
    ) -> Dict:
        """Check if content with given provenance is allowed for action."""
        policy = self.policies.get(provenance, self.policies["user_direct"])
        
        if action == "use_in_llm_context":
            return {
                "allowed": policy["allowed_in_llm_context"],
                "requires_approval": policy["requires_user_approval"],
                "max_length": policy["max_context_length"],
                "must_redact": policy["must_be_redacted"]
            }
        
        return {"allowed": True, "requires_approval": False}
    
    def enforce_length_limit(self, content: str, provenance: str) -> str:
        """Enforce length limits based on provenance."""
        policy = self.policies.get(provenance, self.policies["user_direct"])
        max_length = policy.get("max_context_length")
        
        if max_length and len(content) > max_length:
            logger.warning(
                "Content truncated due to provenance policy",
                provenance=provenance,
                original_length=len(content),
                max_length=max_length
            )
            return content[:max_length] + "... [truncated]"
        
        return content
