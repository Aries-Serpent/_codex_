"""
Test Sanitize

Test module for sanitize.
"""

#!/usr/bin/env python3
"""Tests for sanitize utility."""
from src.utils.sanitize import sanitize_prompt


def test_sanitize_escapes_script_tag():
    """Test that script tags are escaped to prevent XSS."""
    prompt = '<script>alert("x")</script>'
    escaped = sanitize_prompt(prompt)
    # Expect the script tag characters to be escaped so they cannot execute when rendered
    assert "<script>" not in escaped
    assert "&lt;script&gt;" in escaped


def test_sanitize_none_returns_empty_string():
    """Test that None input returns empty string."""
    assert sanitize_prompt(None) == ""


def test_sanitize_escapes_quotes():
    """Test that both single and double quotes are escaped."""
    prompt = """<a href="javascript:alert('xss')">click</a>"""
    escaped = sanitize_prompt(prompt)
    assert '"' not in escaped
    assert "'" not in escaped
    assert "&quot;" in escaped
    assert "&#x27;" in escaped


def test_sanitize_escapes_ampersand():
    """Test that ampersand is properly escaped."""
    prompt = "foo & bar"
    escaped = sanitize_prompt(prompt)
    assert "&amp;" in escaped


def test_sanitize_preserves_safe_text():
    """Test that safe text without HTML chars passes through."""
    prompt = "This is a safe prompt without HTML"
    escaped = sanitize_prompt(prompt)
    # Should still be readable
    assert "This is a safe prompt without HTML" == escaped
