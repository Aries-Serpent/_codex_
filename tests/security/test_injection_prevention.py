import pytest

from src.security import SecurityError, validate_input


def test_sql_injection_blocked() -> None:
    malicious = "'; DROP TABLE users; --"
    with pytest.raises(SecurityError):
        validate_input(malicious, input_type="sql")


def test_xss_script_sanitized() -> None:
    xss = "<script>alert('xss')</script>"
    safe = validate_input(xss, input_type="html")
    assert "<script>" not in safe
    assert "&lt;script&gt;" in safe
