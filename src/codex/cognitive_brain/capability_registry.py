"""Capability Registry — model capability cache with TTL.

Provides a thread-safe, TTL-aware registry of model capability profiles.
Each profile declares which session configuration parameters a model supports,
enabling the ModelNegotiator to gate unsupported parameters before they reach
the session-creation API and cause runtime errors such as:

    Request session.create failed … Model 'claude-haiku-4.5' does not support
    reasoning effort configuration

Usage::

    registry = CapabilityRegistry()
    profile = registry.get("claude-haiku-4.5")
    if not profile.supports_reasoning_effort:
        config.pop("reasoning_effort", None)
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Capability profile
# ---------------------------------------------------------------------------

# Known models that support extended-thinking / reasoning-effort config.
# Populated from public Anthropic/OpenAI documentation; update as APIs evolve.
_REASONING_EFFORT_SUPPORTED: frozenset[str] = frozenset(
    {
        "claude-opus-4.5",
        "claude-opus-4.6",
        "claude-opus-4.7",
        "claude-opus-4.8",
        "claude-opus-4.8-fast",
        "claude-opus-5",
        "claude-sonnet-4.5",
        "claude-sonnet-4.6",
        "claude-sonnet-5",
        "claude-fable-5",
        "o1",
        "o1-mini",
        "o1-preview",
        "o3",
        "o3-mini",
        "o4-mini",
        "gemini-3.1-pro-preview",
        "gpt-5.3-codex",
        "gpt-5.4",
        "gpt-5.4-mini",
        "gpt-5.5",
        "gpt-5.6-luna",
        "gpt-5.6-sol",
        "gpt-5.6-terra",
        "grok-4.5",
        "kimi-k2.7-code",
    }
)

# Models that are lightweight / fast and may lack extended reasoning.
_LIGHTWEIGHT_MODELS: frozenset[str] = frozenset(
    {
        "claude-haiku-4.5",
        "gpt-5-mini",
        "gemini-3.5-flash",
        "gemini-3.6-flash",
        "mai-code-1-flash-picker",
    }
)


@dataclass
class ModelCapabilityProfile:
    """Declared capability profile for a single model identifier."""

    model_id: str
    supports_reasoning_effort: bool = False
    supports_streaming: bool = True
    supports_tools: bool = True
    supports_vision: bool = False
    is_lightweight: bool = False
    max_output_tokens: int = 8192
    # Additional arbitrary capability flags for forward-compatibility.
    extra_flags: Dict[str, bool] = field(default_factory=dict)

    def supports(self, capability: str) -> bool:
        """Return True if this profile declares *capability* as supported."""
        if capability == "reasoning_effort":
            return self.supports_reasoning_effort
        if capability == "streaming":
            return self.supports_streaming
        if capability == "tools":
            return self.supports_tools
        if capability == "vision":
            return self.supports_vision
        return self.extra_flags.get(capability, False)


def _build_default_profile(model_id: str) -> ModelCapabilityProfile:
    """Construct a best-effort capability profile from the known-models tables."""
    reasoning = model_id in _REASONING_EFFORT_SUPPORTED
    lightweight = model_id in _LIGHTWEIGHT_MODELS
    return ModelCapabilityProfile(
        model_id=model_id,
        supports_reasoning_effort=reasoning,
        is_lightweight=lightweight,
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class CapabilityRegistry:
    """Thread-safe, TTL-aware cache of :class:`ModelCapabilityProfile` objects.

    On a cache miss the registry synthesises a default profile from the
    built-in known-models tables.  Externally obtained profiles (e.g., from a
    live ``models.list`` API call) can be injected via :meth:`register`.

    Parameters
    ----------
    ttl_seconds:
        How long a cached profile is considered fresh.  Defaults to 3600 s.
    """

    def __init__(self, ttl_seconds: float = 3600.0) -> None:
        self._ttl = ttl_seconds
        self._lock = threading.Lock()
        # Maps model_id → (profile, expiry_epoch)
        self._cache: Dict[str, tuple[ModelCapabilityProfile, float]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, model_id: str) -> ModelCapabilityProfile:
        """Return the :class:`ModelCapabilityProfile` for *model_id*.

        Returns a cached profile if still fresh, otherwise rebuilds from
        the built-in tables and stores it.
        """
        with self._lock:
            entry = self._cache.get(model_id)
            if entry is not None:
                profile, expiry = entry
                if time.monotonic() < expiry:
                    return profile
                logger.debug("Capability cache expired for model=%s; rebuilding", model_id)

            profile = _build_default_profile(model_id)
            self._cache[model_id] = (profile, time.monotonic() + self._ttl)
            logger.debug(
                "Capability profile built: model=%s reasoning_effort=%s",
                model_id,
                profile.supports_reasoning_effort,
            )
            return profile

    def register(self, profile: ModelCapabilityProfile) -> None:
        """Inject or replace a profile in the cache, resetting its TTL."""
        with self._lock:
            self._cache[profile.model_id] = (profile, time.monotonic() + self._ttl)
            logger.info("Registered capability profile for model=%s", profile.model_id)

    def invalidate(self, model_id: Optional[str] = None) -> None:
        """Evict *model_id* from the cache (or clear all entries if None)."""
        with self._lock:
            if model_id is None:
                self._cache.clear()
                logger.debug("Capability cache cleared")
            else:
                self._cache.pop(model_id, None)
                logger.debug("Capability cache invalidated for model=%s", model_id)

    def all_known(self) -> Dict[str, ModelCapabilityProfile]:
        """Return a snapshot of all currently cached profiles."""
        with self._lock:
            return {mid: p for mid, (p, _) in self._cache.items()}


# ---------------------------------------------------------------------------
# Module-level default registry (singleton)
# ---------------------------------------------------------------------------

_default_registry: Optional[CapabilityRegistry] = None
_registry_lock = threading.Lock()


def get_default_registry() -> CapabilityRegistry:
    """Return the process-level default :class:`CapabilityRegistry`."""
    global _default_registry
    with _registry_lock:
        if _default_registry is None:
            _default_registry = CapabilityRegistry()
    return _default_registry
