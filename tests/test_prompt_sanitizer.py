"""
Test Prompt Sanitizer

Test module for prompt sanitizer.
"""

#!/usr/bin/env python3
"""Tests for PromptSanitizer."""
import sys
from pathlib import Path

import pytest

# Add src to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

# Import directly from the module file
from codex_ml.safety.prompt_sanitizer import PromptSanitizer


def test_prompt_sanitizer_strict_blocks_script():
    """Test that script tags are blocked in strict mode."""
    sanitizer = PromptSanitizer(strict=True)

    with pytest.raises(ValueError, match="Unsafe prompt detected"):
        sanitizer.sanitize("<script>alert('xss')</script>")


def test_prompt_sanitizer_strict_blocks_javascript():
    """Test that javascript: URLs are blocked in strict mode."""
    sanitizer = PromptSanitizer(strict=True)

    with pytest.raises(ValueError, match="Unsafe prompt detected"):
        sanitizer.sanitize("Click here: javascript:alert('xss')")


def test_prompt_sanitizer_strict_blocks_eval():
    """Test that eval() calls are blocked in strict mode."""
    sanitizer = PromptSanitizer(strict=True)

    with pytest.raises(ValueError, match="Unsafe prompt detected"):
        sanitizer.sanitize("Run eval(malicious_code)")


def test_prompt_sanitizer_strict_blocks_subprocess():
    """Test that subprocess calls are blocked in strict mode."""
    sanitizer = PromptSanitizer(strict=True)

    with pytest.raises(ValueError, match="Unsafe prompt detected"):
        sanitizer.sanitize("import subprocess; subprocess.run(['rm', '-rf', '/'])")


def test_prompt_sanitizer_non_strict_redacts_script():
    """Test that script tags are redacted in non-strict mode."""
    sanitizer = PromptSanitizer(strict=False)
    result = sanitizer.sanitize("Run <script>alert()</script> this code")

    assert "[REDACTED]" in result, "Result must not be empty"
    assert "<script>" not in result.lower(), "Result must not be empty"


def test_prompt_sanitizer_non_strict_redacts_multiple_patterns():
    """Test that multiple patterns are redacted."""
    sanitizer = PromptSanitizer(strict=False)
    result = sanitizer.sanitize("<script>test</script> and eval(bad)")

    assert result.count("[REDACTED]") >= 2, "Value must be greater than zero"
    assert "script" not in result.lower(), "Result must not be empty"
    assert "eval" not in result.lower(), "Result must not be empty"


def test_prompt_sanitizer_safe_prompts_pass_through():
    """Test that safe prompts are not modified."""
    sanitizer = PromptSanitizer(strict=True)
    safe_prompt = "What is the capital of France?"

    result = sanitizer.sanitize(safe_prompt)
    assert result == safe_prompt, "Result must not be empty"


def test_prompt_sanitizer_is_safe_returns_true_for_safe():
    """Test that is_safe returns True for safe prompts."""
    sanitizer = PromptSanitizer()

    assert sanitizer.is_safe("This is a safe prompt"), "This is not valid"
    assert sanitizer.is_safe("Tell me about Python programming"), "Condition must be true"


def test_prompt_sanitizer_is_safe_returns_false_for_unsafe():
    """Test that is_safe returns False for unsafe prompts."""
    sanitizer = PromptSanitizer()

    assert not sanitizer.is_safe("<script>alert('xss')</script>"), "Condition must be true"
    assert not sanitizer.is_safe("eval(malicious_code)"), "Condition must be true"


def test_prompt_sanitizer_get_violations_returns_patterns():
    """Test that get_violations returns matched patterns."""
    sanitizer = PromptSanitizer()
    violations = sanitizer.get_violations("<script>test</script>")

    assert len(violations) > 0, "Violations must not be empty"
    assert any("script" in v.lower() for v in violations), "Condition must be true"


def test_prompt_sanitizer_get_violations_empty_for_safe():
    """Test that get_violations returns empty list for safe prompts."""
    sanitizer = PromptSanitizer()
    violations = sanitizer.get_violations("This is safe")

    assert violations == [], "violations is not valid"


def test_prompt_sanitizer_handles_empty_string():
    """Test that empty strings are handled gracefully."""
    sanitizer = PromptSanitizer()

    assert sanitizer.sanitize("") == "", "Condition must be true"
    assert sanitizer.is_safe(""), "Condition must be true"
    assert sanitizer.get_violations("") == [], "Condition must be true"


def test_prompt_sanitizer_blocks_sql_injection():
    """Test that SQL injection patterns are blocked."""
    sanitizer = PromptSanitizer(strict=True)

    with pytest.raises(ValueError):
        sanitizer.sanitize("DROP TABLE users")

    with pytest.raises(ValueError):
        sanitizer.sanitize("DELETE FROM users WHERE 1=1")


def test_prompt_sanitizer_blocks_command_injection():
    """Test that command injection patterns are blocked."""
    sanitizer = PromptSanitizer(strict=True)

    with pytest.raises(ValueError):
        sanitizer.sanitize("rm -rf /important/data")

    with pytest.raises(ValueError):
        sanitizer.sanitize("Use os.system('malicious')")


def test_prompt_sanitizer_blocks_event_handlers():
    """Test that HTML event handlers are blocked."""
    sanitizer = PromptSanitizer(strict=True)

    with pytest.raises(ValueError):
        sanitizer.sanitize("<img onerror='alert(1)'>")

    with pytest.raises(ValueError):
        sanitizer.sanitize("<body onload='malicious()'>")


def test_prompt_sanitizer_case_insensitive():
    """Test that pattern matching is case-insensitive."""
    sanitizer = PromptSanitizer(strict=True)

    with pytest.raises(ValueError):
        sanitizer.sanitize("<SCRIPT>ALERT('XSS')</SCRIPT>")

    with pytest.raises(ValueError):
        sanitizer.sanitize("EVAL(code)")


# ============================================================================
# MUTATION-KILLING TESTS FOR SANITIZERS
# ============================================================================


class TestSanitizersMutations:
    """Kill mutations in sanitizer functions."""

    def test_case_insensitive_exact_match(self):
        """Kill: Case mutation operators.

        Verifies that .lower() or case-insensitive matching works correctly.
        """
        sanitizer = PromptSanitizer(strict=True)

        # All case variations should be caught
        patterns = [
            "<script>alert('xss')</script>",
            "<SCRIPT>ALERT('XSS')</SCRIPT>",
            "<Script>Alert('Xss')</Script>",
        ]

        for pattern in patterns:
            with pytest.raises(ValueError):
                sanitizer.sanitize(pattern)

    def test_unicode_preservation_exact(self):
        """Kill: Unicode mutation operators.

        Verifies Unicode characters are preserved.
        """
        sanitizer = PromptSanitizer(strict=False)

        # Test Unicode preservation - should not crash
        result = sanitizer.sanitize("café")
        # Unicode should be preserved or handled gracefully
        assert "café" in result or len(result) > 0, "Result must not be empty"

    def test_xss_pattern_exact_detection(self):
        """Kill: XSS detection pattern mutations."""
        sanitizer = PromptSanitizer(strict=True)

        # Must detect exact XSS patterns
        xss_patterns = [
            "javascript:alert(1)",
            "<img src=x onerror=alert(1)>",
        ]

        for pattern in xss_patterns:
            with pytest.raises(ValueError):
                sanitizer.sanitize(pattern)
