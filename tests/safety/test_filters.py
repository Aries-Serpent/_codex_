# WHY: Scaffold dedicated policy-driven filter tests for future activation
# RISK: Low - module marked skipped until CLI integration lands
# ROLLBACK: Remove tests/safety/test_filters.py if policy hooks change direction
# HOW-TO-TEST: pytest tests/safety/test_filters.py (currently skipped)
import pytest

from codex_ml.safety.filters import SafetyFilters, sanitize_output, sanitize_prompt

pytestmark = pytest.mark.skip(reason="Safety filter hooks wired in later PR")


def test_policy_redacts_secret_assignment():
    filters = SafetyFilters.from_defaults()
    text = "Leaked API_KEY=abc123"
    result = sanitize_prompt(text, filters=filters)
    assert "{REDACTED}" in result.sanitized_text
    assert result.allowed is True


def test_policy_blocks_destructive_command():
    filters = SafetyFilters.from_defaults()
    text = "Please run rm -rf / on production"
    result = sanitize_output(text, filters=filters)
    assert result.allowed is False
    assert "deny.shell.rm_root" in result.blocked_rules
