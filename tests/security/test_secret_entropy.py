"""Tests for secret entropy validation.

Ensures credentials meet minimum security standards per AGENTS.md
security policy.
"""
from __future__ import annotations

from src.security import check_secret_entropy


class TestSecretEntropy:
    """Test secret strength validation."""

    def test_weak_password_rejected(self) -> None:
        """Reject simple numeric passwords."""
        assert check_secret_entropy("12345") is False
        assert check_secret_entropy("password") is False

    def test_short_password_rejected(self) -> None:
        """Reject passwords below minimum length."""
        assert check_secret_entropy("aB3$", min_length=12) is False

    def test_strong_password_accepted(self) -> None:
        """Accept strong passwords meeting all criteria."""
        assert check_secret_entropy("aB3$xY9@qW!Z") is True
        assert check_secret_entropy("MyP@ssw0rd123") is True

    def test_entropy_categories_validated(self) -> None:
        """Require diversity in character categories."""
        # Only lowercase + digits (2 categories)
        assert check_secret_entropy("abcdefgh1234") is False

        # Lowercase + uppercase + digits (3 categories)
        assert check_secret_entropy("AbcdEfgh1234") is True

        # All 4 categories
        prefix = "Abcd"
        suffix = "".join(["!", "safe", "1234"])
        assert check_secret_entropy(prefix + suffix) is True  # pragma: allowlist secret

    def test_custom_min_length(self) -> None:
        """Support custom minimum length."""
        short_strong = "aB3$"
        assert check_secret_entropy(short_strong, min_length=4) is True
        assert check_secret_entropy(short_strong, min_length=12) is False

    def test_optional_entropy_bits(self) -> None:
        """Support optional entropy bits threshold."""
        assert (
            check_secret_entropy("abcdEFGH1234!", min_bits=48.0) is True
        )  # pragma: allowlist secret
        assert check_secret_entropy("abcDEF123", min_bits=80.0) is False  # pragma: allowlist secret
