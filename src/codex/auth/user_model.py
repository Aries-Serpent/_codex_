"""
User domain model for the Codex authentication layer.

Extracted from :mod:`codex.auth.user_store` so that the ``UserRepository``
ABC and concrete backends can import :class:`User` without creating a
circular dependency with :mod:`codex.auth.user_store`.

All external code should continue to import :class:`User` and
:class:`PasswordHasher` from :mod:`codex.auth.user_store` (backward-compat
re-exports are maintained there).
"""

from __future__ import annotations

import hashlib
import hmac as _hmac
import os
import time
from dataclasses import dataclass, field
from typing import Optional

# PBKDF2 parameters — increasing ITERATIONS raises cost for attackers.
_PBKDF2_HASH = "sha256"
_PBKDF2_ITERATIONS = 600_000
_SALT_BYTES = 32
_HASH_BYTES = 32


@dataclass
class User:
    """Mutable user identity record (password, active flag, and updated_at are updated in-place)."""

    user_id: str
    username: str
    email: str
    password_hash: str  # "<salt_hex>:<hash_hex>"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    is_active: bool = True
    roles: list[str] = field(default_factory=lambda: ["user"])
    display_name: Optional[str] = None

    # ------------------------------------------------------------------ #
    # Convenience                                                          #
    # ------------------------------------------------------------------ #

    def has_role(self, role: str) -> bool:
        """Return True if the user has *role*."""
        return role in self.roles

    def to_dict(self) -> dict:
        """Serialise to a dict, omitting the password hash."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "roles": list(self.roles),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class PasswordHasher:
    """
    Secure PBKDF2-SHA256 password hasher.

    Uses only the Python standard library so no additional packages are
    required.
    """

    def __init__(
        self,
        iterations: int = _PBKDF2_ITERATIONS,
        salt_bytes: int = _SALT_BYTES,
        hash_bytes: int = _HASH_BYTES,
    ) -> None:
        self._iterations = iterations
        self._salt_bytes = salt_bytes
        self._hash_bytes = hash_bytes

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def hash(self, password: str) -> str:
        """
        Hash *password* and return ``"<salt_hex>:<hash_hex>"``.

        Args:
            password: Plain-text password.

        Returns:
            Salted hash string suitable for storage.

        Raises:
            ValueError: If *password* is empty.
        """
        if not password:
            raise ValueError("Password must not be empty")

        salt = os.urandom(self._salt_bytes)
        digest = hashlib.pbkdf2_hmac(
            _PBKDF2_HASH,
            password.encode("utf-8"),
            salt,
            self._iterations,
            dklen=self._hash_bytes,
        )
        return f"{salt.hex()}:{digest.hex()}"

    def verify(self, password: str, stored_hash: str) -> bool:
        """
        Verify *password* against *stored_hash*.

        Uses :func:`hmac.compare_digest` to avoid timing side-channels.

        Args:
            password: Plain-text password to check.
            stored_hash: Value previously returned by :meth:`hash`.

        Returns:
            ``True`` if the password matches, ``False`` otherwise.
        """
        try:
            salt_hex, hash_hex = stored_hash.split(":", 1)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(hash_hex)
        except (ValueError, AttributeError):
            # Malformed hash — treat as verification failure
            return False

        digest = hashlib.pbkdf2_hmac(
            _PBKDF2_HASH,
            password.encode("utf-8"),
            salt,
            self._iterations,
            dklen=self._hash_bytes,
        )
        # Constant-time comparison
        return _hmac.compare_digest(digest, expected)
