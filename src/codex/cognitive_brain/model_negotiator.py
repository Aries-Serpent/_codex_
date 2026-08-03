"""Model Negotiator — safe session configuration for heterogeneous model runtimes.

The negotiator intercepts any session configuration dict before it reaches the
session-creation API and strips or rewrites parameters that the target model
does not support.  This prevents runtime errors such as:

    Request session.create failed … Model 'claude-haiku-4.5' does not support
    reasoning effort configuration

Key responsibilities
--------------------
1. Query :class:`~cognitive_brain.capability_registry.CapabilityRegistry` for
   the model's capability profile.
2. Strip unsupported parameters (``reasoning_effort``, etc.).
3. When the preferred model is incompatible with required capabilities, select
   a ranked fallback from a configurable compatibility matrix.
4. Emit structured telemetry for every negotiation decision.

Usage::

    negotiator = ModelNegotiator()
    safe_cfg = negotiator.negotiate(
        model_id="claude-haiku-4.5",
        session_config={"reasoning_effort": "high", "max_tokens": 4096},
        required_capabilities=["reasoning_effort"],
    )
    # safe_cfg["model"] == "claude-sonnet-5"  (fallback chosen)
    # safe_cfg["reasoning_effort"]  → absent (unsupported on original model)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from .capability_registry import (
    CapabilityRegistry,
    ModelCapabilityProfile,
    get_default_registry,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Ordered fallback chain: when the requested model cannot satisfy required
# capabilities, candidates are tried in this order.
_DEFAULT_FALLBACK_CHAIN: List[str] = [
    "claude-sonnet-5",
    "claude-sonnet-4.6",
    "claude-opus-4.8",
    "claude-opus-4.7",
    "claude-opus-5",
    "gpt-5.5",
    "gpt-5.4",
    "gemini-3.1-pro-preview",
    "grok-4.5",
]

# Parameters gated by capability flags.
_CAPABILITY_GATES: Dict[str, str] = {
    "reasoning_effort": "supports_reasoning_effort",
    "thinking": "supports_reasoning_effort",  # Anthropic extended-thinking alias
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class NegotiationResult:
    """Output of a single :class:`ModelNegotiator` negotiation pass."""

    original_model_id: str
    resolved_model_id: str
    safe_config: Dict[str, Any]
    stripped_params: List[str] = field(default_factory=list)
    fallback_used: bool = False
    capability_profile: Optional[ModelCapabilityProfile] = None
    notes: List[str] = field(default_factory=list)

    @property
    def model_changed(self) -> bool:
        """True if the resolved model differs from the originally requested model."""
        return self.original_model_id != self.resolved_model_id


# ---------------------------------------------------------------------------
# Negotiator
# ---------------------------------------------------------------------------


class ModelNegotiator:
    """Gate and rewrite session configuration for model capability safety.

    Parameters
    ----------
    registry:
        Capability registry to consult.  Defaults to the process-level
        singleton if not provided.
    fallback_chain:
        Ordered list of model IDs to try when the primary model cannot satisfy
        required capabilities.
    """

    def __init__(
        self,
        registry: Optional[CapabilityRegistry] = None,
        fallback_chain: Optional[Sequence[str]] = None,
    ) -> None:
        self._registry = registry or get_default_registry()
        self._fallback_chain: List[str] = (
            list(fallback_chain) if fallback_chain is not None else list(_DEFAULT_FALLBACK_CHAIN)
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def negotiate(
        self,
        model_id: str,
        session_config: Dict[str, Any],
        required_capabilities: Optional[Sequence[str]] = None,
    ) -> NegotiationResult:
        """Return a :class:`NegotiationResult` with a safe session config.

        Steps
        -----
        1. Look up capability profile for *model_id*.
        2. Remove config keys that the model does not support.
        3. If *required_capabilities* cannot be met, select a fallback model.
        4. Return the cleaned config alongside negotiation metadata.

        Parameters
        ----------
        model_id:
            The originally requested model identifier.
        session_config:
            Raw session configuration dict (will not be mutated).
        required_capabilities:
            Capabilities that *must* be present.  If the model lacks any,
            a fallback is selected.
        """
        required = list(required_capabilities or [])
        safe_cfg = dict(session_config)
        profile = self._registry.get(model_id)
        stripped: List[str] = []
        notes: List[str] = []

        # Step 1 — strip unsupported gated parameters.
        for param, cap_attr in _CAPABILITY_GATES.items():
            if param in safe_cfg:
                model_supports = getattr(profile, cap_attr, False)
                if not model_supports:
                    safe_cfg.pop(param)
                    stripped.append(param)
                    notes.append(
                        f"Stripped '{param}': model '{model_id}' does not support {cap_attr}"
                    )
                    logger.info(
                        "Model negotiation: stripped param=%s from model=%s "
                        "(missing capability=%s)",
                        param,
                        model_id,
                        cap_attr,
                    )

        # Step 2 — check required capabilities; select fallback if needed.
        unmet = [cap for cap in required if not profile.supports(cap)]
        fallback_used = False
        resolved_model = model_id

        if unmet:
            fallback = self._select_fallback(unmet)
            if fallback is not None:
                fallback_profile = self._registry.get(fallback)
                notes.append(
                    f"Required capabilities {unmet} not met by '{model_id}'; "
                    f"selected fallback '{fallback}'"
                )
                logger.warning(
                    "Model negotiation: fallback model=%s chosen for unmet_caps=%s (original=%s)",
                    fallback,
                    unmet,
                    model_id,
                )
                resolved_model = fallback
                profile = fallback_profile
                fallback_used = True

                # Re-strip for fallback model as well.
                for param, cap_attr in _CAPABILITY_GATES.items():
                    if param in safe_cfg:
                        fb_supports = getattr(fallback_profile, cap_attr, False)
                        if not fb_supports and param not in stripped:
                            safe_cfg.pop(param)
                            stripped.append(param)
                            notes.append(
                                f"Stripped '{param}' from fallback '{fallback}' too"
                            )
            else:
                notes.append(
                    f"No fallback found for unmet capabilities {unmet}; "
                    "proceeding with stripped config on original model"
                )
                logger.error(
                    "Model negotiation: no suitable fallback for unmet_caps=%s; "
                    "proceeding with model=%s",
                    unmet,
                    model_id,
                )

        result = NegotiationResult(
            original_model_id=model_id,
            resolved_model_id=resolved_model,
            safe_config=safe_cfg,
            stripped_params=stripped,
            fallback_used=fallback_used,
            capability_profile=profile,
            notes=notes,
        )
        logger.debug(
            "Negotiation complete: original=%s resolved=%s stripped=%s fallback=%s",
            model_id,
            resolved_model,
            stripped,
            fallback_used,
        )
        return result

    def safe_session_config(
        self,
        model_id: str,
        session_config: Dict[str, Any],
        required_capabilities: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
        """Convenience wrapper returning only the cleaned config dict.

        The resolved model ID is injected under the key ``"model"`` so callers
        can pass the dict directly to the session-creation API.
        """
        result = self.negotiate(model_id, session_config, required_capabilities)
        out = dict(result.safe_config)
        out["model"] = result.resolved_model_id
        return out

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _select_fallback(self, required_capabilities: List[str]) -> Optional[str]:
        """Return the first fallback model that satisfies *required_capabilities*."""
        for candidate in self._fallback_chain:
            profile = self._registry.get(candidate)
            if all(profile.supports(cap) for cap in required_capabilities):
                return candidate
        return None
