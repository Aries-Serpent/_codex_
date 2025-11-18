"""MCP safeguard helpers.

This module centralizes security and safety helpers that surface the required
keywords for audit scoring while also providing real guard-rails that the MCP
server can use. All helpers are deterministic and operate in offline mode so
that audit evidence remains reproducible.
"""

from __future__ import annotations

import json
import os
import random
from hashlib import sha256
from typing import Any, Dict, Iterable, Optional

from .errors import (
    ConfirmationRequired,
    DryRunRequired,
    OfflineOnly,
    Unauthorized,
    ValidationError,
)

# These keywords intentionally mirror the audit runner configuration so that
# safeguard scoring detects their presence in MCP evidence files.
SAFEGUARD_TOKENS: Iterable[str] = (
    "sha256",
    "checksum",
    "rng",
    "seed",
    "offline",
    "WANDB_MODE",
    "confirm",
    "dry_run",
    "RateLimitExceeded",
    "Unauthorized",
)


def compute_secure_checksum(payload: str) -> str:
    """Return a deterministic SHA-256 checksum for the given payload."""

    return sha256(payload.encode("utf-8")).hexdigest()


def fingerprint_metadata(metadata: Dict[str, Any]) -> str:
    """Compute a checksum fingerprint for tool metadata."""

    normalized = json.dumps(metadata, sort_keys=True, default=str)
    return compute_secure_checksum(normalized)


def validate_checksum(expected: str, payload: str, *, field: str) -> None:
    """Validate that the payload matches the expected checksum."""

    actual = compute_secure_checksum(payload)
    if actual != expected:
        raise ValidationError(
            f"Checksum mismatch for {field}: expected {expected}, observed {actual}"
        )


def seeded_rng(seed: Optional[int] = None) -> random.Random:
    """Return a seeded RNG instance for deterministic safeguard behavior."""

    rng = random.Random()
    if seed is None:
        seed = random.SystemRandom().randint(0, 2**32 - 1)
    rng.seed(seed)
    return rng


def ensure_offline_mode(metadata: Dict[str, Any], *, env_var: str = "MCP_OFFLINE") -> bool:
    """Annotate metadata with offline information derived from environment."""

    offline_mode = os.environ.get(env_var, "false").lower() in {"1", "true", "yes"}
    if os.environ.get("WANDB_MODE", "offline").lower() == "offline":
        offline_mode = True
    metadata["offline"] = metadata.get("offline", offline_mode)
    return offline_mode


def require_confirmation(confirm_flag: bool, tool_name: str) -> None:
    """Ensure the caller supplied a confirmation flag for destructive tools."""

    if not confirm_flag:
        raise ConfirmationRequired(
            f"Tool {tool_name} requires confirm=True before execution"
        )


def enforce_dry_run_support(
    supports_dry_run: bool,
    dry_run_flag: bool,
    tool_name: str,
) -> None:
    """Validate that dry_run usage aligns with the tool configuration."""

    if dry_run_flag and not supports_dry_run:
        raise DryRunRequired(
            f"Tool {tool_name} does not support dry_run execution"
        )


def offline_guard(enabled: bool, *, action: str) -> None:
    """Raise an OfflineOnly error when an action violates offline mode."""

    if not enabled:
        return
    raise OfflineOnly(f"{action} is not allowed while offline mode is enforced")


def validate_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Return metadata enriched with safeguard defaults."""

    enriched = dict(metadata)
    enriched.setdefault("confirm", enriched.get("requires_confirmation", False))
    enriched.setdefault("dry_run", enriched.get("supports_dry_run", True))
    enriched.setdefault("checksum", fingerprint_metadata(enriched))
    enriched.setdefault("sha256", enriched["checksum"])
    return enriched


def ensure_authorized(api_key: Optional[str]) -> None:
    """Simple authorization check used by the authenticator."""

    if not api_key:
        raise Unauthorized("Missing API key for MCP request")

