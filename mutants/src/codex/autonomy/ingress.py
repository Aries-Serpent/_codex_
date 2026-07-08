"""
Phase 3 — Ingress Gateway

Normalises and gates all inbound autonomous-agent events regardless of
origin (issue_comment, repository_dispatch, workflow_dispatch,
pull_request_target, webhook, API proxy, CLI).

Every ingress path MUST pass through this gateway before routing to an
execution surface.  The gateway:

1. Validates event schema and required fields.
2. Checks actor against the allowlist.
3. Verifies an anti-replay nonce.
4. Consults the autonomy registry for mode and surface permissions.
5. Returns an :class:`IngressDecision` with allow/deny + reason.

Usage::

    from codex.autonomy.ingress import IngressEvent, IngressGateway

    gw  = IngressGateway.default()
    evt = IngressEvent(
        event_type="issue_comment",
        actor="mbaetiong",
        payload={"body": "@copilot fix the coverage", "nonce": "abc123"},
        source_surface="AUT-007",
    )
    decision = gw.evaluate(evt)
    if not decision.allowed:
        raise RuntimeError(decision.reason)

Blueprint: .codex/docs/AUTONOMY_BLUEPRINT.md — Phase 3
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .registry import AutonomyRegistry, ControlClass

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

# Default actor allowlist — can be overridden via CODEX_ALLOWED_ACTORS env var
_DEFAULT_ALLOWED_ACTORS = frozenset(
    {
        "mbaetiong",
        "github-actions[bot]",
        "copilot-swe-agent[bot]",
        "github-copilot[bot]",
    }
)

# Replay window: reject events with the same nonce seen within this many seconds
_REPLAY_WINDOW_SECONDS = 300  # 5 minutes

# Event types and their associated default control class
_EVENT_CONTROL_CLASS: dict[str, ControlClass] = {
    "issue_comment": ControlClass.ADVISORY_WRITE,
    "repository_dispatch": ControlClass.REPO_STATE_WRITE,
    "workflow_dispatch": ControlClass.REPO_STATE_WRITE,
    "pull_request_target": ControlClass.ADVISORY_WRITE,
    "webhook": ControlClass.EXTERNAL_BRIDGE,
    "api_proxy": ControlClass.EXTERNAL_BRIDGE,
    "cli": ControlClass.REMOTE_EXEC,
    "schedule": ControlClass.READ_ONLY,
    "push": ControlClass.READ_ONLY,
}


class IngressResult(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    DRY_RUN = "dry_run"  # allowed by policy but dry_run=true so mutations skipped


@dataclass
class IngressEvent:
    """Normalised representation of an inbound event."""

    event_type: str  # e.g. "issue_comment"
    actor: str  # triggering GitHub user/bot
    payload: dict[str, Any] = field(default_factory=dict)
    source_surface: str = ""  # e.g. "AUT-007"
    control_class: Optional[str] = None  # override auto-derived class
    nonce: str = ""  # anti-replay token
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        # Auto-derive control class from event type if not provided
        if not self.control_class:
            derived = _EVENT_CONTROL_CLASS.get(self.event_type, ControlClass.REPO_STATE_WRITE)
            self.control_class = derived.value
        # Extract nonce from payload if not set directly
        if not self.nonce:
            self.nonce = str(self.payload.get("nonce", ""))


@dataclass(frozen=True)
class IngressDecision:
    """Result of gateway evaluation."""

    result: IngressResult
    reason: str
    event: IngressEvent
    policy_version: str = ""

    @property
    def allowed(self) -> bool:
        return self.result in (IngressResult.ALLOW, IngressResult.DRY_RUN)

    @property
    def is_dry_run(self) -> bool:
        return self.result == IngressResult.DRY_RUN


class IngressGateway:
    """
    Validates and gates inbound autonomous-agent events.

    Parameters
    ----------
    registry:
        Autonomy state registry.  Loaded from default path if not supplied.
    allowed_actors:
        Frozenset of actor names permitted to trigger autonomous actions.
        If *None*, read from ``CODEX_ALLOWED_ACTORS`` env var or fall back to
        the built-in default set.
    """

    def __init__(
        self,
        registry: Optional[AutonomyRegistry] = None,
        allowed_actors: Optional[frozenset[str]] = None,
    ) -> None:
        self._registry = registry or AutonomyRegistry.load()
        self._allowed_actors = allowed_actors or self._load_allowed_actors()
        self._seen_nonces: dict[str, float] = {}  # nonce → first-seen timestamp

    @classmethod
    def default(cls) -> "IngressGateway":
        """Convenience factory using default registry and actor list."""
        return cls()

    def evaluate(self, event: IngressEvent) -> IngressDecision:
        """
        Evaluate whether *event* should be allowed through.

        Checks are executed in order; the first failure short-circuits.
        """
        reg = self._registry
        pv = reg.policy_version

        # 1. Kill-switch
        if reg.kill_switch:
            return IngressDecision(
                result=IngressResult.DENY,
                reason="kill_switch=true",
                event=event,
                policy_version=pv,
            )

        # 2. Mode = OFF
        if reg.autonomy_mode.value == "OFF":
            return IngressDecision(
                result=IngressResult.DENY,
                reason="autonomy_mode=OFF",
                event=event,
                policy_version=pv,
            )

        # 3. Actor allowlist
        if event.actor not in self._allowed_actors:
            return IngressDecision(
                result=IngressResult.DENY,
                reason=f"actor '{event.actor}' not in allowlist",
                event=event,
                policy_version=pv,
            )

        # 4. Anti-replay nonce
        if event.nonce:
            nonce_key = self._nonce_key(event)
            now = time.time()
            self._purge_expired_nonces(now)
            if nonce_key in self._seen_nonces:
                return IngressDecision(
                    result=IngressResult.DENY,
                    reason=f"replay detected — nonce '{event.nonce}' already seen",
                    event=event,
                    policy_version=pv,
                )
            self._seen_nonces[nonce_key] = now

        # 5. Schema validation — required fields
        missing = self._validate_schema(event)
        if missing:
            return IngressDecision(
                result=IngressResult.DENY,
                reason=f"schema validation failed — missing fields: {missing}",
                event=event,
                policy_version=pv,
            )

        # 6. Policy permission check via registry
        allowed, policy_reason = reg.is_permitted(
            event.source_surface,
            event.control_class or "ADVISORY_WRITE",
            actor=event.actor,
        )
        if not allowed:
            return IngressDecision(
                result=IngressResult.DENY,
                reason=policy_reason,
                event=event,
                policy_version=pv,
            )

        # 7. Dry-run flag
        if reg.dry_run:
            return IngressDecision(
                result=IngressResult.DRY_RUN,
                reason=f"dry_run=true — {policy_reason}",
                event=event,
                policy_version=pv,
            )

        return IngressDecision(
            result=IngressResult.ALLOW,
            reason=policy_reason,
            event=event,
            policy_version=pv,
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _load_allowed_actors() -> frozenset[str]:
        raw = os.environ.get("CODEX_ALLOWED_ACTORS", "")
        if raw.strip():
            actors = frozenset(a.strip() for a in raw.split(",") if a.strip())
            logger.debug("IngressGateway: loaded %d allowed actors from env", len(actors))
            return actors
        return _DEFAULT_ALLOWED_ACTORS

    @staticmethod
    def _nonce_key(event: IngressEvent) -> str:
        """Stable key combining actor + event_type + nonce."""
        raw = f"{event.actor}:{event.event_type}:{event.nonce}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _purge_expired_nonces(self, now: float) -> None:
        expired = [k for k, t in self._seen_nonces.items() if now - t > _REPLAY_WINDOW_SECONDS]
        for k in expired:
            del self._seen_nonces[k]

    @staticmethod
    def _validate_schema(event: IngressEvent) -> list[str]:
        """Return list of missing required fields (empty = valid)."""
        missing = []
        if not event.event_type:
            missing.append("event_type")
        if not event.actor:
            missing.append("actor")
        return missing
