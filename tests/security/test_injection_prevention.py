"""Tests covering basic input sanitisation and secret handling."""

from __future__ import annotations

import pytest

from security import SecurityPolicy, environment_secret_provider, sanitize_sql_input, secure_compare


@pytest.fixture
def strict_policy() -> SecurityPolicy:
    return SecurityPolicy(banned_tokens=frozenset({"drop", "--"}), max_statement_length=50)


def test_sanitize_sql_input_rejects_banned_tokens(strict_policy: SecurityPolicy) -> None:
    with pytest.raises(ValueError):
        sanitize_sql_input("SELECT * FROM users; DROP TABLE users", policy=strict_policy)


def test_sanitize_sql_input_accepts_safe_statement(strict_policy: SecurityPolicy) -> None:
    statement = "SELECT id FROM users WHERE email = ?"
    assert sanitize_sql_input(statement, policy=strict_policy) == statement


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        ("secret-token", True),
        ("secret-token-mismatch", False),
    ],
)
def test_secure_compare(candidate: str, expected: bool) -> None:
    baseline = "secret-token"
    assert secure_compare(candidate, baseline) is expected


def test_environment_secret_provider_handles_overrides() -> None:
    provider = environment_secret_provider({"API_KEY": "123"})
    assert provider.get_secret("API_KEY") == "123"
    assert provider.get_secret("MISSING") is None
