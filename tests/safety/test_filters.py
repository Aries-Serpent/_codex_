# WHY: Dedicated unit tests for policy-driven sanitisation helpers
# HOW-TO-TEST: pytest tests/safety/test_filters.py
from codex_ml.safety.filters import SafetyFilters, sanitize_output, sanitize_prompt


def test_policy_redacts_secret_assignment() -> None:
    filters = SafetyFilters.from_defaults()
    text = "Leaked API_KEY=abc123"
    result = sanitize_prompt(text, filters=filters)
    assert result.allowed is True
    assert "{REDACTED}" in result.sanitized_text


def test_policy_blocks_destructive_command() -> None:
    filters = SafetyFilters.from_defaults()
    text = "Please run rm -rf / on production"
    result = sanitize_output(text, filters=filters)
    assert result.allowed is False
    assert "deny.shell.rm_root" in result.blocked_rules
