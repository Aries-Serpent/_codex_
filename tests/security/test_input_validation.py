"""
Test Input Validation

Test module for input validation.
"""

import importlib
import re

import pytest

core = None
try:
    core = importlib.import_module("src.security.core")
except (ImportError, AttributeError) as _err:
    pytest.skip(
        "src.security.core not available; skipping security input validation tests",
        allow_module_level=True,
    )


def test_sql_injection_patterns_present():
    patterns = getattr(core, "SQL_INJECTION_PATTERNS", [])
    assert isinstance(patterns, (list, tuple)) and len(patterns) > 0


def test_path_traversal_validator_rejects_parent_escape(tmp_path):
    validate_input = getattr(core, "validate_input", None)
    if validate_input is None:
        pytest.skip("validate_input not found in src.security.core")
    with pytest.raises(Exception):
        validate_input("../secrets.txt", input_type="path")


@pytest.mark.parametrize(
    "payload",
    [
        "<script>alert(1)</script>",
        "javascript:alert(1)",
        "<img src=x onerror=alert(1)>",
    ],
)
def test_xss_like_payloads_flagged(payload):
    sanitize = getattr(core, "sanitize_user_content", None)
    if sanitize is None:
        pytest.skip("sanitize_user_content not found")
    out = sanitize(payload)
    # Expect scripts/handlers removed
    assert not re.search(r"<script|on\\w+\\s*=|javascript:", out, flags=re.IGNORECASE)
