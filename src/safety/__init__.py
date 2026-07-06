"""Lightweight safety bundle with explicit policy defaults and documentation.

This placeholder package surfaces a minimal safety profile so downstream
modules can introspect defaults even when richer policy modules are not
installed in the environment. The defaults reflect conservative settings and
are intentionally small to avoid importing heavy optional dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .network_policy import PolicyViolationError, enforce_network_policy


@dataclass(frozen=True)
class SafetyProfile:
    """Static defaults for safety-aware features."""

    min_entropy_bits: float = 48.0
    max_secret_age_days: int = 30
    redact_pii: bool = True
    allow_network_calls: bool = False


DEFAULT_SAFETY_PROFILE: Final[SafetyProfile] = SafetyProfile()

__all__ = [
    "DEFAULT_SAFETY_PROFILE",
    "PolicyViolationError",
    "SafetyProfile",
    "enforce_network_policy",
]
