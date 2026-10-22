"""Unified evidence store for the improvement loop.

Consolidates the loop's persistence behind one durable, versioned
interface:

- **Events and results** (SDK evidence contract) persisted as JSONL with
  the event ID as the idempotency key.
- **Outcomes** recorded per event for the confidence-update seam.
- **Circuit breakers** demote/disable patterns that repeatedly fail or
  go stale without deleting their audit history.

The store defaults to a durable on-disk location (``.codex/improvement/
evidence.jsonl``); an in-memory directory is only ever used when a caller
explicitly points at one (e.g. tests via ``tmp_path``). Nothing here is
``:memory:``-by-default.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

logger = logging.getLogger(__name__)

EVIDENCE_STORE_SCHEMA_VERSION = "1.0.0"
DEFAULT_STORE_PATH = Path(".codex") / "improvement" / "evidence.jsonl"

# Circuit-breaker defaults.
DEFAULT_MAX_CONSECUTIVE_FAILURES = 3
DEFAULT_STALE_AFTER_DAYS = 90


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class CircuitBreaker:
    """Per-pattern circuit breaker driven by verified outcomes."""

    max_consecutive_failures: int = DEFAULT_MAX_CONSECUTIVE_FAILURES
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS
    _consecutive_failures: int = 0
    _disabled: bool = False
    _disable_reason: str = ""

    def record(self, outcome: str) -> None:
        """Record a verified outcome (``success``/``regression``/``rollback``)."""
        if outcome == "success":
            self._consecutive_failures = 0
        elif outcome in ("regression", "rollback"):
            self._consecutive_failures += 1
            if self._consecutive_failures >= self.max_consecutive_failures:
                self._disabled = True
                self._disable_reason = (
                    f"{self._consecutive_failures} consecutive failing outcomes"
                )

    def check_stale(self, last_used_iso: str) -> bool:
        """Disable when the pattern has been idle beyond the staleness window."""
        try:
            last = datetime.fromisoformat(last_used_iso.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return False
        age_days = (datetime.now(timezone.utc) - last).days
        if age_days > self.stale_after_days:
            self._disabled = True
            self._disable_reason = f"stale: unused for {age_days} days"
        return self._disabled

    @property
    def disabled(self) -> bool:
        return self._disabled

    @property
    def reason(self) -> str:
        return self._disable_reason


@dataclass(slots=True)
class EvidenceStore:
    """Durable event/result/outcome store with a read-only audit trail."""

    path: Path = DEFAULT_STORE_PATH
    _records: List[Dict[str, Any]] = field(default_factory=list)
    _event_ids: set = field(default_factory=set)
    _outcomes: Dict[str, Mapping[str, Any]] = field(default_factory=dict)
    _breakers: Dict[str, CircuitBreaker] = field(default_factory=dict)
    _pattern_events: Dict[str, set[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.path = Path(self.path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not self.path.exists():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            self._records.append(record)
            if record.get("kind") == "event":
                self._event_ids.add(record["payload"]["event_id"])
            elif record.get("kind") == "outcome":
                payload = record["payload"]
                self._outcomes[payload["event_id"]] = payload
                pat = payload.get("pattern_id")
                if pat:
                    self._pattern_events.setdefault(pat, set()).add(payload["event_id"])

    def _append(self, kind: str, payload: Mapping[str, Any]) -> None:
        record = {
            "schema_version": EVIDENCE_STORE_SCHEMA_VERSION,
            "kind": kind,
            "recorded_at": _utcnow(),
            "payload": dict(payload),
        }
        self._records.append(record)
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, default=str) + "\n")

    # ------------------------------------------------------------------
    # Events and outcomes
    # ------------------------------------------------------------------

    def record_event(self, event_dict: Mapping[str, Any]) -> bool:
        """Persist an event once (idempotent on ``event_id``)."""

        event_id = str(event_dict.get("event_id", ""))
        if not event_id:
            raise ValueError("event record requires an event_id")
        if event_id in self._event_ids:
            return False
        self._event_ids.add(event_id)
        self._append("event", event_dict)
        return True

    def record_outcome(
        self,
        *,
        event_id: str,
        merged: bool,
        outcome: str,
        pattern_id: Optional[str] = None,
        patch_hash: Optional[str] = None,
        details: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Persist a measured post-merge outcome for an event.

        Identical measurements are deduplicated, while an explicit transition
        from a pending/unmerged state to a final outcome still updates the
        record. This keeps the outcome store authoritative without discarding
        later measurements for the same event.
        """

        existing = self._outcomes.get(event_id)
        if existing is not None:
            if existing.get("outcome") == outcome and existing.get("merged") == merged:
                return
            payload = {
                "event_id": event_id,
                "merged": merged,
                "outcome": outcome,
                "pattern_id": pattern_id,
                "patch_hash": patch_hash,
                "details": dict(details or {}),
            }
            self._outcomes[event_id] = payload
            self._append("outcome", payload)
        else:
            payload = {
                "event_id": event_id,
                "merged": merged,
                "outcome": outcome,
                "pattern_id": pattern_id,
                "patch_hash": patch_hash,
                "details": dict(details or {}),
            }
            self._outcomes[event_id] = payload
            self._append("outcome", payload)
        if pattern_id and merged:
            self.breaker(pattern_id).record(outcome)
            self._pattern_events.setdefault(pattern_id, set()).add(event_id)

    def outcome_for(self, event_id: str) -> Optional[Mapping[str, Any]]:
        """Return the recorded outcome for an event (read-only)."""

        return self._outcomes.get(event_id)

    def record(self, kind: str, event_id: str, payload: Mapping[str, Any]) -> None:
        """Persist an auxiliary evidence record (execution, pr, confidence).

        These kinds complete the audit trail the evaluator inspects; the
        payload always carries the originating ``event_id`` so the trail
        stays linked end-to-end. Idempotency is enforced on ``event``.
        """

        if not event_id:
            raise ValueError("evidence record requires an event_id")
        body = {"event_id": event_id, **dict(payload)}
        self._append(kind, body)

    def seen(self, event_id: str) -> bool:
        return event_id in self._event_ids

    # ------------------------------------------------------------------
    # Circuit breakers
    # ------------------------------------------------------------------

    def breaker(self, pattern_id: str) -> CircuitBreaker:
        if pattern_id not in self._breakers:
            self._breakers[pattern_id] = CircuitBreaker()
        return self._breakers[pattern_id]

    def pattern_enabled(self, pattern_id: str, last_used_iso: str = "") -> bool:
        """Whether a pattern may still drive proposals (fail-closed)."""

        breaker = self.breaker(pattern_id)
        if breaker.disabled:
            return False
        if last_used_iso and breaker.check_stale(last_used_iso):
            return False
        return not breaker.disabled

    def disable_reason(self, pattern_id: str) -> str:
        return self.breaker(pattern_id).reason

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    def audit_trail(self, event_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Read-only view of the recorded evidence, optionally per event."""

        if event_id is None:
            return list(self._records)
        return [
            r for r in self._records if r.get("payload", {}).get("event_id") == event_id
        ]

    def backup(self, destination: Path) -> Path:
        """Copy the store to *destination* (restore by pointing at the copy)."""

        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            destination.write_bytes(self.path.read_bytes())
        else:
            destination.write_text("", encoding="utf-8")
        return destination

    def stats(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "events": len(self._event_ids),
            "outcomes": len(self._outcomes),
            "disabled_patterns": [
                pid for pid, b in self._breakers.items() if b.disabled
            ],
        }
