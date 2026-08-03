"""Session Guard — central session.create safety wrapper.

Every session creation that uses the Cognitive Brain runtime **must** pass
through :class:`SessionGuard`.  The guard:

1. Calls :class:`~model_negotiator.ModelNegotiator` to strip unsupported
   parameters (e.g. ``reasoning_effort`` on ``claude-haiku-4.5``).
2. Records a telemetry event with decision tracing fields
   (``decision_id``, ``turn_id``, ``task_id``).
3. Provides a typed result including the negotiated config and diagnostics.

This eliminates the residual class of errors:

    Request session.create failed … Model 'claude-haiku-4.5' does not support
    reasoning effort configuration

Usage::

    guard = SessionGuard()
    result = guard.create_session("claude-haiku-4.5", raw_config)
    # result.safe_config is ready to pass to the session API
    response = my_session_client.create(**result.safe_config)
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from src.codex.cognitive_brain.capability_registry import CapabilityRegistry, get_default_registry
from src.codex.cognitive_brain.model_negotiator import ModelNegotiator, NegotiationResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass
class SessionCreateResult:
    """Output of :meth:`SessionGuard.create_session`.

    Attributes
    ----------
    safe_config:
        Session configuration dict with unsupported params stripped and the
        resolved model ID injected under the key ``"model"``.
    negotiation:
        Full negotiation metadata from :class:`ModelNegotiator`.
    decision_id:
        Unique identifier for this guard invocation (for forensics replay).
    turn_id:
        Caller-supplied turn identifier, forwarded into telemetry.
    task_id:
        Caller-supplied task identifier, forwarded into telemetry.
    duration_ms:
        Wall-clock time for the guard invocation in milliseconds.
    notes:
        Human-readable summary of negotiation decisions.
    """

    safe_config: Dict[str, Any]
    negotiation: NegotiationResult
    decision_id: str
    turn_id: Optional[str]
    task_id: Optional[str]
    duration_ms: float
    notes: List[str] = field(default_factory=list)

    @property
    def resolved_model(self) -> str:
        return self.negotiation.resolved_model_id

    @property
    def params_stripped(self) -> List[str]:
        return self.negotiation.stripped_params

    @property
    def fallback_used(self) -> bool:
        return self.negotiation.fallback_used


# ---------------------------------------------------------------------------
# Guard
# ---------------------------------------------------------------------------


class SessionGuard:
    """Intercept and safety-check all session.create calls.

    Parameters
    ----------
    negotiator:
        :class:`ModelNegotiator` to use.  Defaults to a fresh instance
        backed by the default :class:`CapabilityRegistry`.
    registry:
        Registry to use when *negotiator* is not provided.
    telemetry:
        Optional :class:`~telemetry.CognitiveTelemetry` instance for event
        recording.  If None the guard operates without telemetry.
    """

    def __init__(
        self,
        negotiator: Optional[ModelNegotiator] = None,
        registry: Optional[CapabilityRegistry] = None,
        telemetry: Any = None,
    ) -> None:
        _registry = registry or get_default_registry()
        self._negotiator = negotiator or ModelNegotiator(registry=_registry)
        self._telemetry = telemetry

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_session(
        self,
        model_id: str,
        session_config: Dict[str, Any],
        required_capabilities: Optional[Sequence[str]] = None,
        *,
        turn_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> SessionCreateResult:
        """Gate and rewrite *session_config* for *model_id*.

        Parameters
        ----------
        model_id:
            Requested model identifier.
        session_config:
            Raw session configuration dict (will not be mutated).
        required_capabilities:
            Capabilities that must be available on the resolved model.
        turn_id:
            Caller's turn identifier (for telemetry / forensics).
        task_id:
            Caller's task identifier (for telemetry / forensics).

        Returns
        -------
        SessionCreateResult
            Contains the safe config to pass to the session API plus
            diagnostic metadata.
        """
        decision_id = str(uuid.uuid4())
        t0 = time.monotonic()

        negotiation = self._negotiator.negotiate(model_id, session_config, required_capabilities)
        safe_cfg = dict(negotiation.safe_config)
        safe_cfg["model"] = negotiation.resolved_model_id

        duration_ms = (time.monotonic() - t0) * 1000

        notes: List[str] = list(negotiation.notes)
        if negotiation.model_changed:
            notes.append(
                f"Model changed: {negotiation.original_model_id!r} → "
                f"{negotiation.resolved_model_id!r}"
            )
        if negotiation.stripped_params:
            notes.append(f"Stripped params: {negotiation.stripped_params}")

        result = SessionCreateResult(
            safe_config=safe_cfg,
            negotiation=negotiation,
            decision_id=decision_id,
            turn_id=turn_id,
            task_id=task_id,
            duration_ms=duration_ms,
            notes=notes,
        )

        self._emit_telemetry(result)

        logger.info(
            "SessionGuard: decision_id=%s model=%s→%s stripped=%s fallback=%s "
            "turn_id=%s task_id=%s duration_ms=%.1f",
            decision_id,
            model_id,
            negotiation.resolved_model_id,
            negotiation.stripped_params,
            negotiation.fallback_used,
            turn_id,
            task_id,
            duration_ms,
        )
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _emit_telemetry(self, result: SessionCreateResult) -> None:
        if self._telemetry is None:
            return
        try:
            from src.codex.cognitive_brain.telemetry import TelemetryEvent

            self._telemetry.record(
                TelemetryEvent(
                    event_type="session_guard",
                    model_id=result.resolved_model,
                    duration_ms=result.duration_ms,
                    success=True,
                    decision_id=result.decision_id,
                    turn_id=result.turn_id,
                    task_id=result.task_id,
                    payload={
                        "original_model": result.negotiation.original_model_id,
                        "resolved_model": result.resolved_model,
                        "stripped_params": result.params_stripped,
                        "fallback_used": result.fallback_used,
                    },
                    notes=result.notes,
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("SessionGuard telemetry emit failed: %s", exc)


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------


_default_guard: Optional[SessionGuard] = None


def get_default_guard() -> SessionGuard:
    """Return the process-level default :class:`SessionGuard`."""
    global _default_guard
    if _default_guard is None:
        _default_guard = SessionGuard()
    return _default_guard


def safe_create_session(
    model_id: str,
    session_config: Dict[str, Any],
    required_capabilities: Optional[Sequence[str]] = None,
    *,
    turn_id: Optional[str] = None,
    task_id: Optional[str] = None,
) -> SessionCreateResult:
    """Convenience wrapper calling the default :class:`SessionGuard`."""
    return get_default_guard().create_session(
        model_id,
        session_config,
        required_capabilities,
        turn_id=turn_id,
        task_id=task_id,
    )


def reset_default_guard() -> None:
    """Reset the singleton (for testing only)."""
    global _default_guard
    _default_guard = None
