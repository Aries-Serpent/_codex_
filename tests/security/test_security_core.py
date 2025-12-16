"""Smoke coverage for security.core."""

from __future__ import annotations

from pathlib import Path

import pytest

from security import core


def test_sanitize_user_content_html() -> None:
    result = core.sanitize_user_content("<script>alert('x')</script>")
    assert "<" not in result


def test_validate_input_sql_rejects() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("1; DROP TABLE users;", input_type="sql")


def test_validate_path_traversal_blocked() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("../../etc/passwd", input_type="path")


def test_rate_limiter_allows_then_blocks() -> None:
    calls = []

    @core.rate_limiter(calls=2, period=10, key_func=lambda *_: "k")
    def fn(x: int) -> int:
        calls.append(x)
        return x

    assert fn(1) == 1
    assert fn(2) == 2
    with pytest.raises(core.SecurityError):
        fn(3)


def test_validate_input_json_blocks_prototype() -> None:
    with pytest.raises(core.SecurityError):
        core.validate_input("__proto__", input_type="json")
