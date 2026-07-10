"""Tests for secret entropy validation.

Ensures credentials meet minimum security standards per .codex/archive/deprecated/AGENTS.md
security policy.
"""

from __future__ import annotations

from security import check_secret_entropy


class TestSecretEntropy:
    """Test secret strength validation."""

    def test_weak_password_rejected(self) -> None:
        """Reject simple numeric passwords."""
        assert check_secret_entropy("12345") is False, "Condition must be true"
        assert check_secret_entropy("password") is False, "Condition must be true"

    def test_short_password_rejected(self) -> None:
        """Reject passwords below minimum length."""
        assert check_secret_entropy("aB3$", min_length=12) is False

    def test_strong_password_accepted(self) -> None:
        """Accept strong passwords meeting all criteria."""
        assert check_secret_entropy("aB3$xY9@qW!Z") is True, "Condition must be true"
        assert check_secret_entropy("MyP@ssw0rd123") is True, "Condition must be true"

    def test_entropy_categories_validated(self) -> None:
        """Require diversity in character categories."""
        # Only lowercase + digits (2 categories)
        assert check_secret_entropy("abcdefgh1234") is False, "Condition must be true"

        # Lowercase + uppercase + digits (3 categories)
        assert check_secret_entropy("AbcdEfgh1234") is True, "Condition must be true"

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
