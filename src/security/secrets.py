"""Secret management helpers used across infrastructure tooling."""

from __future__ import annotations

import math
import secrets
import string
import time
from collections.abc import Iterable
from dataclasses import dataclass, field

from .core import SecurityError


def _character_pool(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def check_secret_entropy(value: str, *, min_bits: float = 48.0) -> bool:
    """Return True when the provided secret meets the entropy threshold."""

    if not value:
        return False
    pool = _character_pool(value)
    estimated_bits = len(value) * math.log2(pool)
    return estimated_bits >= min_bits


@dataclass
class SecretRotationPolicy:
    """Policy defining rotation thresholds for secrets."""

    min_entropy_bits: float = 48.0
    max_age_seconds: int = 60 * 60 * 24 * 30
    history_size: int = 5


@dataclass
class SecretRotationState:
    """Book-keeping information for a managed secret."""

    identifier: str
    last_rotated: float = field(default_factory=lambda: time.time())
    history: list[str] = field(default_factory=list)

    def remember(self, secret: str) -> None:
        self.history.append(secret)
        if len(self.history) > SecretRotationPolicy().history_size:
            self.history = self.history[-SecretRotationPolicy().history_size :]


def rotate_secret(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(candidate, min_bits=policy.min_entropy_bits):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def assert_secret_not_reused(secret: str, history: Iterable[str]) -> None:
    if secret in history:
        raise SecurityError("Secret reuse detected")
