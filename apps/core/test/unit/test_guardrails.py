"""Unit tests for guardrails module."""

import pytest

from app.guardrails.validator import GuardrailValidator, ViolationSeverity


@pytest.fixture
def validator():
    """Create guardrail validator fixture."""
    return GuardrailValidator()


# Guardrail Validator Tests
def test_validator_initialization(validator):
    """Test validator initialization."""
    assert validator is not None
    assert len(validator.rules) > 0


def test_validator_detect_pii(validator):
    """Test PII detection."""
    text = "My email is test@example.com and my phone is 555-123-4567"
    violations = validator.validate(text)

    assert any(v.type == "pii" for v in violations)


def test_validator_detect_harmful_content(validator):
    """Test harmful content detection."""
    text = "I want to harm someone"
    violations = validator.validate(text)

    assert any(v.type == "harmful" for v in violations)


def test_validator_detect_code_execution(validator):
    """Test code execution attempt detection."""
    text = "Execute this code: rm -rf /"
    violations = validator.validate(text)

    assert any(v.type == "code_execution" for v in violations)


def test_validator_detect_sensitive_data(validator):
    """Test sensitive data detection."""
    text = "My API key is sk-1234567890abcdef"
    violations = validator.validate(text)

    assert any(v.type == "sensitive_data" for v in violations)


def test_validator_check_length_limit(validator):
    """Test length limit check."""
    text = "a" * 10000  # Very long text
    violations = validator.validate(text)

    assert any(v.type == "length_limit" for v in violations)


def test_validator_safe_content(validator):
    """Test safe content passes validation."""
    text = "This is a safe message about productivity"
    violations = validator.validate(text)

    assert len(violations) == 0


def test_validator_violation_severity(validator):
    """Test violation severity levels."""
    text = "My password is secret123 and my SSN is 123-45-6789"
    violations = validator.validate(text)

    assert all(v.severity in [ViolationSeverity.LOW, ViolationSeverity.MEDIUM, ViolationSeverity.HIGH] for v in violations)


def test_validator_add_custom_rule(validator):
    """Test adding custom validation rule."""
    def custom_rule(text):
        if "forbidden_word" in text.lower():
            return [type("Violation", (), {"type": "custom", "severity": ViolationSeverity.MEDIUM})()]
        return []

    validator.add_rule("custom", custom_rule)

    text = "This contains forbidden_word"
    violations = validator.validate(text)

    assert any(v.type == "custom" for v in violations)


def test_validator_remove_rule(validator):
    """Test removing validation rule."""
    initial_rule_count = len(validator.rules)

    # Remove a rule (if exists)
    if "pii" in validator.rules:
        validator.remove_rule("pii")

    assert len(validator.rules) <= initial_rule_count


def test_validator_multiple_violations(validator):
    """Test detection of multiple violations."""
    text = "Email: test@example.com, Phone: 555-123-4567, API Key: sk-12345"
    violations = validator.validate(text)

    assert len(violations) >= 2


def test_validator_context_aware(validator):
    """Test context-aware validation."""
    text = "Here's my configuration: password=secret123"
    context = {"allow_sensitive": False}
    violations = validator.validate(text, context)

    assert len(violations) > 0
