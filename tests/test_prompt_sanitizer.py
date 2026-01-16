"""
Test Prompt Sanitizer

Test module for prompt sanitizer.
"""

#!/usr/bin/env python3
"""Tests for PromptSanitizer."""
import pytest
import sys
from pathlib import Path

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

    assert "[REDACTED]" in result
    assert "<script>" not in result.lower()


def test_prompt_sanitizer_non_strict_redacts_multiple_patterns():
    """Test that multiple patterns are redacted."""
    sanitizer = PromptSanitizer(strict=False)
    result = sanitizer.sanitize("<script>test</script> and eval(bad)")

    assert result.count("[REDACTED]") >= 2
    assert "script" not in result.lower()
    assert "eval" not in result.lower()


def test_prompt_sanitizer_safe_prompts_pass_through():
    """Test that safe prompts are not modified."""
    sanitizer = PromptSanitizer(strict=True)
    safe_prompt = "What is the capital of France?"

    result = sanitizer.sanitize(safe_prompt)
    assert result == safe_prompt


def test_prompt_sanitizer_is_safe_returns_true_for_safe():
    """Test that is_safe returns True for safe prompts."""
    sanitizer = PromptSanitizer()

    assert sanitizer.is_safe("This is a safe prompt")
    assert sanitizer.is_safe("Tell me about Python programming")


def test_prompt_sanitizer_is_safe_returns_false_for_unsafe():
    """Test that is_safe returns False for unsafe prompts."""
    sanitizer = PromptSanitizer()

    assert not sanitizer.is_safe("<script>alert('xss')</script>")
    assert not sanitizer.is_safe("eval(malicious_code)")


def test_prompt_sanitizer_get_violations_returns_patterns():
    """Test that get_violations returns matched patterns."""
    sanitizer = PromptSanitizer()
    violations = sanitizer.get_violations("<script>test</script>")

    assert len(violations) > 0
    assert any("script" in v.lower() for v in violations)


def test_prompt_sanitizer_get_violations_empty_for_safe():
    """Test that get_violations returns empty list for safe prompts."""
    sanitizer = PromptSanitizer()
    violations = sanitizer.get_violations("This is safe")

    assert violations == []


def test_prompt_sanitizer_handles_empty_string():
    """Test that empty strings are handled gracefully."""
    sanitizer = PromptSanitizer()

    assert sanitizer.sanitize("") == ""
    assert sanitizer.is_safe("")
    assert sanitizer.get_violations("") == []


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
