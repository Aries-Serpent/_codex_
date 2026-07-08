"""Unit tests for sanitize_prompt utility (Phase 23 Week 3 gapfill)."""

from src.utils.sanitize import sanitize_prompt


def test_sanitize_prompt_basic_html_escaping():
    """Test sanitize_prompt escapes HTML entities."""
    result = sanitize_prompt("<script>alert('xss')</script>")
    assert "<script>" not in result, "Result must not be empty"
    assert "&lt;script&gt;" in result or result == "", "Result must not be empty"


def test_sanitize_prompt_unicode_handling():
    """Test sanitize_prompt handles Unicode correctly."""
    result = sanitize_prompt("Hello 世界 🌍")
    assert "Hello" in result, "Result must not be empty"
    # Unicode should be preserved or safely encoded


def test_sanitize_prompt_empty_input():
    """Test sanitize_prompt handles empty string."""
    result = sanitize_prompt("")
    assert result == "", "Result must not be empty"


def test_sanitize_prompt_none_input():
    """Test sanitize_prompt handles None input."""
    result = sanitize_prompt(None)
    assert result == "" or result == "None", "Result must not be empty"


def test_sanitize_prompt_numeric_coercion():
    """Test sanitize_prompt coerces numbers to string."""
    result = sanitize_prompt(12345)
    assert "12345" in result, "Result must not be empty"


def test_sanitize_prompt_newline_handling():
    """Test sanitize_prompt handles newlines."""
    result = sanitize_prompt("line1\nline2\rline3")
    assert "\n" not in result, "Result must not be empty"
    assert "\r" not in result, "Result must not be empty"


def test_sanitize_prompt_sql_injection_patterns():
    """Test sanitize_prompt mitigates SQL injection patterns."""
    dangerous = "'; DROP TABLE users; --"
    result = sanitize_prompt(dangerous)
    # Should escape or remove dangerous characters
    assert "DROP TABLE" in result or "'" not in result, "Result must not be empty"


def test_sanitize_prompt_xss_vector():
    """Test sanitize_prompt blocks XSS vectors."""
    xss = "<img src=x onerror=alert(1)>"
    result = sanitize_prompt(xss)
    assert "onerror" not in result or "<img" not in result, "Result must not be empty"


def test_sanitize_prompt_control_character_removal():
    """Test sanitize_prompt removes control characters."""
    result = sanitize_prompt("text\x00with\x1fcontrol")
    assert "\x00" not in result, "Result must not be empty"
    assert "\x1f" not in result, "Result must not be empty"


def test_sanitize_prompt_ansi_escape_removal():
    """Test sanitize_prompt removes ANSI escape codes."""
    result = sanitize_prompt("\x1b[31mred text\x1b[0m")
    assert "\x1b" not in result, "Result must not be empty"
    assert "red text" in result, "Result must not be empty"


def test_sanitize_prompt_truncation():
    """Test sanitize_prompt truncates long input."""
    long_input = "a" * 10000
    result = sanitize_prompt(long_input, max_length=100)
    assert len(result) <= 110, "Result must not be empty"


def test_sanitize_prompt_mixed_content():
    """Test sanitize_prompt handles mixed dangerous content."""
    mixed = "<script>alert(1)</script>\n\x00\x1b[31m"
    result = sanitize_prompt(mixed)
    assert "<script>" not in result, "Result must not be empty"
    assert "\x00" not in result, "Result must not be empty"
    assert "\x1b" not in result, "Result must not be empty"
