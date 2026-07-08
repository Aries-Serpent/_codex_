"""Logging sanitization integration tests (Phase 23 Week 3)."""

import pytest

from utils.log_sanitizer import sanitize_dict_for_log, sanitize_log_input
from utils.sanitize import sanitize_prompt


@pytest.mark.integration
def test_end_to_end_log_sanitization():
    """Test complete log sanitization pipeline."""
    dangerous_input = "User input:\nline1\x00\x1b[31mcolored\x1b[0m"

    sanitized = sanitize_log_input(dangerous_input)

    assert "\n" not in sanitized, "Condition must be true"
    assert "\x00" not in sanitized, "Condition must be true"
    assert "\x1b" not in sanitized, "Condition must be true"
    assert "User input" in sanitized, "Condition must be true"


@pytest.mark.integration
def test_prompt_to_log_sanitization_chain():
    """Test sanitization chain from prompt to log."""
    user_prompt = "<script>alert(1)</script>\nmalicious"

    # First sanitize for prompt
    prompt_safe = sanitize_prompt(user_prompt)

    # Then sanitize for logging
    log_safe = sanitize_log_input(prompt_safe)

    assert "\n" not in log_safe, "Condition must be true"
    assert "<script>" not in log_safe, "Condition must be true"


@pytest.mark.integration
def test_dict_sanitization_nested_depth():
    """Test deep nested dict sanitization."""
    data = {"level1": {"level2": {"level3": "value\nwith\nnewlines\x00"}}}

    sanitized = sanitize_dict_for_log(data)

    nested_value = sanitized["level1"]["level2"]["level3"]
    assert "\n" not in nested_value, "Value must be initialized"
    assert "\x00" not in nested_value, "Value must be initialized"


@pytest.mark.integration
def test_mixed_content_sanitization():
    """Test sanitization of mixed content types."""
    data = {
        "text": "line1\nline2",
        "number": 12345,
        "nested": {"key": "\x1b[31mred\x1b[0m"},
    }

    sanitized = sanitize_dict_for_log(data)

    assert "\n" not in sanitized["text"], "Condition must be true"
    assert "12345" in sanitized["number"], "Condition must be true"
    assert "\x1b" not in sanitized["nested"]["key"], "Condition must be true"


@pytest.mark.integration
def test_sanitization_preserves_semantic_content():
    """Test sanitization preserves semantic content."""
    original = "Important message with data"
    sanitized = sanitize_log_input(original)

    assert "Important" in sanitized, "Condition must be true"
    assert "message" in sanitized, "Condition must be true"
    assert "data" in sanitized, "Data must not be empty"
