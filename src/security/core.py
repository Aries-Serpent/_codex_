"""Core primitives for enforcing basic security guarantees."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class SecurityPolicy:
    """Declarative representation of simple guardrails.

    The policy tracks a small collection of banned tokens that should never appear in
    user-provided statements as well as a maximum statement length.  This keeps the
    implementation intentionally small while still providing a central place to evolve
    future checks.
    """

    banned_tokens: frozenset[str]
    max_statement_length: int = 10_000

    def is_token_allowed(self, token: str) -> bool:
        """Return ``True`` when ``token`` is acceptable for user supplied content."""

        return token.lower() not in self.banned_tokens

    def validate_statement(self, statement: str) -> None:
        """Raise ``ValueError`` when the supplied statement violates the policy."""

        if len(statement) > self.max_statement_length:
            msg = (
                "statement exceeds maximum length: "
                f"{len(statement)} > {self.max_statement_length}"
            )
            raise ValueError(msg)

        tokens = _tokenize(statement)
        rejected = [token for token in tokens if not self.is_token_allowed(token)]
        if rejected:
            msg = "statement includes banned tokens: " + ", ".join(
                sorted({token.lower() for token in rejected})
            )
            raise ValueError(msg)


def _tokenize(value: str) -> Iterable[str]:
    """Split statements into normalized tokens."""

    return (token.strip().lower() for token in value.replace("\n", " ").split())


DEFAULT_POLICY = SecurityPolicy(
    banned_tokens=frozenset({"drop", "truncate", ";", "--", "/*", "*/"}),
)


def sanitize_sql_input(statement: str, policy: SecurityPolicy | None = None) -> str:
    """Return ``statement`` if it complies with the policy, otherwise raise ``ValueError``."""

    active_policy = policy or DEFAULT_POLICY
    active_policy.validate_statement(statement)
    return statement


def secure_compare(a: str, b: str) -> bool:
    """Perform a timing-attack resistant comparison using constant time semantics."""

    if len(a) != len(b):
        return False

    result = 0
    for char_a, char_b in zip(a.encode("utf-8"), b.encode("utf-8"), strict=True):
        result |= char_a ^ char_b
    return result == 0
