"""Read-only evaluator for the end-to-end recursive self-improvement loop.

This is the executable counterpart to
``.codex/agents/recursive-improvement-evaluator/SPEC.md``. It assesses
whether the full evidence chain for an ``event_id`` is present in an
:class:`~codex.cognitive_brain.evidence_store.EvidenceStore` audit trail:

    signal -> pattern -> proposal -> isolated gates -> PR -> post-merge
    measurement -> confidence update

It is strictly read-only: it never mutates the store, pattern confidence,
patches, or merges. Until every link is evidenced for a run, the verdict
is ``partial``/``unverified`` and the system remains "partially
integrated components," not a confirmed autonomous runtime.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, List, Mapping, Optional

logger = logging.getLogger(__name__)

# Verdicts per the evaluator spec.
COMPLETE = "complete"
PARTIAL = "partial"
UNVERIFIED = "unverified"

# The ordered links of the end-to-end loop.
_REQUIRED_LINKS = (
    "signal",
    "pattern",
    "proposal",
    "gates",
    "pr",
    "post_merge_measurement",
    "confidence_update",
)


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    """Read-only verdict for one improvement event."""

    event_id: str
    verdict: str
    links: Mapping[str, bool] = field(default_factory=dict)
    missing: tuple = ()
    evidence_count: int = 0


def _classify(records: List[dict]) -> dict[str, bool]:
    """Map a flat audit trail onto the loop's required links."""

    links = {link: False for link in _REQUIRED_LINKS}
    for record in records:
        kind = record.get("kind")
        payload = record.get("payload", {})
        if kind == "event":
            signal = payload.get("signal") or {}
            if signal.get("availability") == "measured":
                links["signal"] = True
            if payload.get("pattern"):
                links["pattern"] = True
            if payload.get("proposal"):
                links["proposal"] = True
        elif kind == "execution":
            gates = payload.get("gate_logs") or []
            if payload.get("status") == "verified" and gates:
                links["gates"] = True
        elif kind == "pr":
            if payload.get("merge_state") in ("pr_open", "merged", "reverted"):
                links["pr"] = True
        elif kind == "outcome":
            if payload.get("merged") and payload.get("outcome") in (
                "success",
                "regression",
                "rollback",
            ):
                links["post_merge_measurement"] = True
        elif kind == "confidence":
            links["confidence_update"] = True
    return links


def evaluate_event(store: Any, event_id: str) -> EvaluationReport:
    """Evaluate one event's audit trail. Read-only; never raises."""

    try:
        records = store.audit_trail(event_id)
    except Exception as e:  # noqa: BLE001 - evaluator must not crash the loop
        logger.error("Failed to read audit trail for %s: %s", event_id, e)
        return EvaluationReport(event_id=event_id, verdict=UNVERIFIED, evidence_count=0)

    if not records:
        return EvaluationReport(event_id=event_id, verdict=UNVERIFIED, evidence_count=0)

    links = _classify(records)
    missing = tuple(link for link in _REQUIRED_LINKS if not links[link])
    verdict = COMPLETE if not missing else PARTIAL
    return EvaluationReport(
        event_id=event_id,
        verdict=verdict,
        links=links,
        missing=missing,
        evidence_count=len(records),
    )


def evaluate_store(store: Any) -> List[EvaluationReport]:
    """Evaluate every recorded event. Read-only."""

    event_ids = [
        r["payload"]["event_id"]
        for r in store.audit_trail()
        if r.get("kind") == "event" and r.get("payload", {}).get("event_id")
    ]
    return [evaluate_event(store, eid) for eid in dict.fromkeys(event_ids)]
