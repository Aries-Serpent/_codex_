"""
Moderation Module

This module provides functionality for moderation.

Usage:
    from safety.moderation import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import importlib
import json
import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from codex_ml.safety.filters import SafetyFilters
from codex_ml.utils.error_log import log_error

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prometheus counter — Gap 27 observability requirement
# ---------------------------------------------------------------------------


class _NoopModCounter:
    """No-op counter used when prometheus-client is unavailable."""

    def labels(self, **_: str) -> "_NoopModCounter":
        return self

    def inc(self, amount: float = 1.0) -> None:  # noqa: ARG002
        pass


def _make_moderation_counter() -> Any:
    """Create a Prometheus Counter for moderation decisions, or a noop fallback."""
    try:
        from prometheus_client import Counter

        return Counter(
            "moderation_decisions_total",
            "Total moderation decisions by stage and verdict",
            ["stage", "verdict"],
        )
    except (IOError, OSError):  # pragma: no cover — prometheus-client absent or already registered
        return _NoopModCounter()


_moderation_decisions_total: Any = _make_moderation_counter()


@dataclass
class ModerationSettings:
    """Configuration for pre- and post-flight moderation checks."""

    enabled: bool = False
    provider: str = "offline"
    rules_path: str | None = None
    fail_open: bool = False
    audit_log: str | None = None
    label: str = "default"


@dataclass
class ModerationDecision:
    """Normalized moderation response used by Codex tooling."""

    approved: bool
    stage: str
    provider: str
    reasons: tuple[str, ...] = ()
    matches: tuple[str, ...] = ()
    sanitized_text: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "approved": self.approved,
            "stage": self.stage,
            "provider": self.provider,
            "reasons": list(self.reasons),
            "matches": list(self.matches),
            "sanitized_text": self.sanitized_text,
            "details": self.details,
        }


class ModerationRejection(RuntimeError):
    """Raised when moderation vetoes a prompt or output."""

    def __init__(
        self,
        stage: str,
        decision: ModerationDecision,
        *,
        provider_error: Exception | None = None,
    ) -> None:
        self.stage = stage
        self.decision = decision
        self.provider_error = provider_error
        summary = ", ".join(decision.matches or decision.reasons) or "moderation policy"
        super().__init__(f"Moderation blocked {stage}: {summary}")


class ModerationAdapter:
    """Adapter that coordinates offline rules and optional providers."""

    def __init__(
        self,
        settings: ModerationSettings,
        *,
        default_policy: str | None = None,
    ) -> None:
        self.settings = settings
        self._default_policy = default_policy
        self._filters: SafetyFilters | None = None
        self._provider = self._resolve_provider(settings.provider)
        self._provider_name = settings.provider if self._provider is not None else "offline"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @classmethod
    def from_settings(
        cls, settings: ModerationSettings, *, default_policy: str | None = None
    ) -> ModerationAdapter:
        return cls(settings=settings, default_policy=default_policy)

    @property
    def provider_name(self) -> str:
        return self._provider_name

    def review(self, text: str, *, stage: str) -> ModerationDecision:
        if not self.settings.enabled:
            return ModerationDecision(
                approved=True,
                stage=stage,
                provider="disabled",
                sanitized_text=text,
            )

        provider_error: Exception | None = None
        decision: ModerationDecision | None = None

        if self._provider is not None:
            try:
                decision = self._call_provider(text, stage)
            except (ValueError, TypeError) as exc:  # pragma: no cover - defensive guard
                provider_error = exc
                log_error(
                    "moderation.provider",
                    str(exc),
                    json.dumps({"provider": self.settings.provider, "stage": stage}),
                )

        if decision is None:
            decision = self._offline_review(text, stage)

        # --- Gap 27 observability: record decision in Prometheus counter ---
        verdict = "accepted" if decision.approved else "rejected"
        _moderation_decisions_total.labels(stage=stage, verdict=verdict).inc()

        if not decision.approved:
            self._record_audit(decision, stage=stage, original_text=text, error=provider_error)
            if self.settings.fail_open:
                log_error(
                    "moderation.fail_open",
                    "moderation veto bypassed",
                    json.dumps(
                        {
                            "stage": stage,
                            "provider": decision.provider,
                            "matches": list(decision.matches),
                            "reasons": list(decision.reasons),
                        }
                    ),
                )
        return decision

    def enforce(self, text: str, *, stage: str) -> ModerationDecision:
        decision = self.review(text, stage=stage)
        if not decision.approved and not self.settings.fail_open:
            # Gap 27: record enforcement-path rejection in counter before raising
            _moderation_decisions_total.labels(stage=stage, verdict="enforced_rejected").inc()
            raise ModerationRejection(stage, decision)
        return decision

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _resolve_provider(self, identifier: str | None) -> Callable[..., Any] | None:
        if not identifier or identifier.lower() == "offline":
            return None
        if ":" not in identifier:
            logger.warning("Unknown moderation provider '%s'; using offline rules", identifier)
            return None
        module_name, attr = identifier.split(":", 1)
        try:
            module = importlib.import_module(module_name)
            candidate = getattr(module, attr)
        except (ImportError, AttributeError) as exc:  # pragma: no cover - defensive guard
            logger.warning("Failed to import moderation provider %s: %s", identifier, exc)
            return None
        if not callable(candidate):
            logger.warning("Moderation provider %s is not callable", identifier)
            return None
        return candidate

    def _ensure_filters(self) -> SafetyFilters:
        if self._filters is None:
            policy_path = self.settings.rules_path or self._default_policy
            self._filters = SafetyFilters.from_policy_file(policy_path)
        return self._filters

    def _offline_review(self, text: str, stage: str) -> ModerationDecision:
        filters = self._ensure_filters()
        decision = filters.evaluate(text, stage=stage)
        matches = tuple(m.rule_id or m.description or "" for m in decision.blocking_matches)
        reasons = tuple(
            sorted(
                {
                    r
                    for r in (
                        *(m.description or "" for m in decision.blocking_matches),
                        *(m.severity or "" for m in decision.blocking_matches),
                    )
                    if r
                }
            )
        )
        details = {
            "policy": str(filters.policy_path) if filters.policy_path else None,
            "bypassed": decision.bypassed,
            "blocking_matches": matches,
        }
        sanitized = decision.sanitized_text if decision.sanitized_text else text
        return ModerationDecision(
            approved=decision.allowed,
            stage=stage,
            provider="offline",
            reasons=reasons,
            matches=matches,
            sanitized_text=sanitized,
            details=details,
        )

    def _call_provider(self, text: str, stage: str) -> ModerationDecision | None:
        payload = self._provider(text=text, stage=stage)  # type: ignore[misc]
        return self._normalize_payload(payload, stage)

    def _normalize_payload(self, payload: Any, stage: str) -> ModerationDecision | None:
        if isinstance(payload, ModerationDecision):
            return payload
        if isinstance(payload, Mapping):
            approved = bool(payload.get("approved", False))
            matches = tuple(str(item) for item in payload.get("matches", ()))
            reasons = tuple(str(item) for item in payload.get("reasons", ()))
            provider = str(payload.get("provider") or self._provider_name)
            sanitized = payload.get("sanitized_text") or payload.get("text")
            extra = {
                key: value
                for key, value in payload.items()
                if key
                not in {
                    "approved",
                    "matches",
                    "reasons",
                    "provider",
                    "sanitized_text",
                    "text",
                }
            }
            return ModerationDecision(
                approved=approved,
                stage=stage,
                provider=provider,
                reasons=reasons,
                matches=matches,
                sanitized_text=str(sanitized) if sanitized is not None else None,
                details=extra,
            )
        return None

    def _record_audit(
        self,
        decision: ModerationDecision,
        *,
        stage: str,
        original_text: str,
        error: Exception | None = None,
    ) -> None:
        if not self.settings.audit_log:
            return
        try:
            path = Path(self.settings.audit_log)
            path.parent.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            entry = {
                "event": "moderation.decision",
                "timestamp": timestamp,
                "stage": stage,
                "provider": decision.provider,
                "approved": decision.approved,
                "matches": list(decision.matches),
                "reasons": list(decision.reasons),
                "fail_open": self.settings.fail_open,
                "label": self.settings.label,
                "details": decision.details,
            }
            if decision.sanitized_text is not None:
                entry["sanitized_text"] = decision.sanitized_text
            if error is not None:
                entry["provider_error"] = {
                    "type": type(error).__name__,
                    "message": str(error),
                }
            entry["original_digest"] = self._hash_text(original_text)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except (IOError, OSError):  # pragma: no cover - audit trail is best-effort
            logger.debug("Failed to write moderation audit entry", exc_info=True)

    @staticmethod
    def _hash_text(value: str) -> str:
        try:
            import hashlib

            return hashlib.sha256(value.encode("utf-8", "ignore")).hexdigest()
        except (ValueError, TypeError):  # pragma: no cover - defensive guard
            return ""


__all__ = [
    "ModerationAdapter",
    "ModerationDecision",
    "ModerationRejection",
    "ModerationSettings",
]
