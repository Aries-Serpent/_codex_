"""Keep registration schemas and direct user-store email validation consistent."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from aries_serpent_core.api.auth_routes import RegisterRequest
from aries_serpent_core.auth.user_store import UserStore


@pytest.mark.parametrize(
    "email",
    [
        ".leading@example.com",
        "trailing.@example.com",
        "consecutive..dots@example.com",
        "user@domain..com",
        "user@.domain.com",
    ],
)
def test_malformed_dot_addresses_are_rejected_by_both_interfaces(email):
    """Invalid dots must fail before a user can be persisted or an API call succeeds."""
    with pytest.raises(ValueError, match="Invalid email format"):
        UserStore._validate_email_format(email)
    with pytest.raises(ValidationError, match="Invalid email format"):
        RegisterRequest(
            username="test-user", email=email, password="SecurePass123!"  # pragma: allowlist secret
        )  # pragma: allowlist secret - synthetic test credential


@pytest.mark.parametrize(
    "email",
    [
        "user+tag@example.com",
        "first.last@sub.example.com",
        "\u7528\u6237@\u4f8b\u3048.jp",
    ],
)
def test_supported_email_formats_remain_valid(email):
    """Dot checks preserve tagged, subdomain and Unicode addresses."""
    UserStore._validate_email_format(email)
    request = RegisterRequest(username="test-user", email=email, password="SecurePass123!")
    assert request.email == email.lower()
