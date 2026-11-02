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
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, List, Mapping, Optional

from codex.cognitive_brain.evidence_store import EvidenceIntegrityError, EvidenceStore
from codex.cognitive_brain.outcome_tracking import verified_measurement

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
_GATE_NAMES = frozenset(
    {"compile", "behavior", "tests", "regression", "lint", "typecheck", "security"}
)
_BEHAVIOR_GATES = frozenset({"behavior", "tests", "regression"})


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise EvidenceIntegrityError("missing aware evidence timestamp")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise EvidenceIntegrityError("naive evidence timestamp")
    return result


def _hash(value: Any, length: int) -> bool:
    return isinstance(value, str) and re.fullmatch(rf"[0-9a-f]{{{length}}}", value) is not None


def _identity(payload: Mapping[str, Any], name: str) -> Any:
    details = payload.get("details") or {}
    if not isinstance(details, Mapping):
        raise EvidenceIntegrityError("malformed identity details")
    if name in payload and name in details and payload[name] != details[name]:
        raise EvidenceIntegrityError(f"conflicting {name}")
    return payload.get(name, details.get(name))


def _passing_gates(payload: Mapping[str, Any], proposal: Mapping[str, Any]) -> bool:
    required = payload.get("required_gates", proposal.get("required_gates"))
    if (
        not isinstance(required, list)
        or not required
        or not all(isinstance(name, str) and name in _GATE_NAMES for name in required)
        or len(required) != len(set(required))
        or not set(required).intersection(_BEHAVIOR_GATES)
        or (
            "required_gates" in payload
            and "required_gates" in proposal
            and payload["required_gates"] != proposal["required_gates"]
        )
    ):
        return False
    gates = payload.get("gate_logs")
    if not isinstance(gates, list) or not gates:
        return False
    names: list[str] = []
    for gate in gates:
        if not isinstance(gate, dict):
            return False
        name, command = gate.get("name"), gate.get("command")
        if (
            name not in _GATE_NAMES
            or type(gate.get("returncode")) is not int
            or gate["returncode"] != 0
            or gate.get("status") != "passed"
            or not isinstance(command, (list, tuple))
            or not command
            or not all(isinstance(arg, str) and arg.strip() for arg in command)
            or not _hash(gate.get("output_hash"), 64)
        ):
            return False
        for identity in ("event_id", "patch_hash", "base_sha", "attempt_id"):
            if identity in gate and gate[identity] != payload.get(identity):
                return False
        names.append(name)
    return len(names) == len(set(names)) and set(required).issubset(names)


def _authorized_regression(payload: Mapping[str, Any], proposal: Mapping[str, Any]) -> bool:
    """Require a bound local authority decision and reproducible behavioral delta."""
    authority = payload.get("authority")
    if (
        not isinstance(authority, Mapping)
        or authority.get("authorized") is not True
        or not isinstance(authority.get("reasons"), (list, tuple))
        or authority["reasons"]
        or authority.get("idempotency_key") != payload.get("event_id")
    ):
        return False
    for identity in ("event_id", "base_sha", "patch_hash", "attempt_id"):
        if identity in authority and authority[identity] != payload.get(identity):
            return False
    baselines = payload.get("baseline_gate_logs")
    candidates = payload.get("gate_logs")
    required = payload.get("required_gates", proposal.get("required_gates"))
    if not isinstance(baselines, list) or not baselines or not isinstance(candidates, list):
        return False
    if not isinstance(required, list):
        return False
    by_name = {gate["name"]: gate for gate in candidates}
    baseline_names: list[str] = []
    behavioral_failure = False
    for gate in baselines:
        if not isinstance(gate, Mapping):
            return False
        name, status, code = gate.get("name"), gate.get("status"), gate.get("returncode")
        candidate = by_name.get(name)
        if (
            name not in _GATE_NAMES
            or type(code) is not int
            or not ((status == "passed" and code == 0) or (status == "failed" and code > 0))
            or candidate is None
            or gate.get("command") != candidate["command"]
            or not _hash(gate.get("output_hash"), 64)
        ):
            return False
        for identity in ("event_id", "base_sha", "patch_hash", "attempt_id"):
            if identity in gate and gate[identity] != payload.get(identity):
                return False
        if gate.get("finished_at") is not None and candidate.get("started_at") is not None:
            if _timestamp(gate["finished_at"]) > _timestamp(candidate["started_at"]):
                return False
        baseline_names.append(name)
        if name in _BEHAVIOR_GATES and name in required and status == "failed":
            behavioral_failure = True
    return (
        len(baseline_names) == len(set(baseline_names))
        and set(required).intersection(_BEHAVIOR_GATES).issubset(baseline_names)
        and behavioral_failure
    )


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    """Read-only verdict for one improvement event."""

    event_id: str
    verdict: str
    links: Mapping[str, bool] = field(default_factory=dict)
    missing: tuple = ()
    evidence_count: int = 0
    proof_scope: str = "unknown"


def _classify(
    records: List[dict],
    event_id: str,
    verifier: Optional[Callable[[Mapping[str, Any]], bool]],
    allow_synthetic: bool,
) -> tuple[dict[str, bool], str]:
    """Map a flat audit trail onto the loop's required links."""

    links = {link: False for link in _REQUIRED_LINKS}
    previous_time: Optional[datetime] = None
    for record in records:
        EvidenceStore._validate_record(record)
        if record["payload"]["event_id"] != event_id:
            raise EvidenceIntegrityError("cross-event evidence")
        timestamp = _timestamp(record["recorded_at"])
        if previous_time is not None and timestamp < previous_time:
            raise EvidenceIntegrityError("nonchronological audit records")
        previous_time = timestamp
    events = [r["payload"] for r in records if r["kind"] == "event"]
    if len(events) != 1:
        raise EvidenceIntegrityError("unique originating event required")
    event = events[0]
    if records[0]["kind"] != "event":
        raise EvidenceIntegrityError("evidence precedes originating event")
    signal, pattern, proposal = (event.get(k) or {} for k in ("signal", "pattern", "proposal"))
    if not all(isinstance(value, dict) for value in (signal, pattern, proposal)):
        raise EvidenceIntegrityError("malformed event chain")
    pattern_id, patch_hash = pattern.get("pattern_id"), proposal.get("patch_hash")
    links["signal"] = (
        signal.get("availability") == "measured"
        and bool(signal.get("source") and signal.get("measured_at"))
        and _hash(event.get("sha"), 40)
        and isinstance(event.get("repo"), str)
        and bool(event["repo"].strip())
    )
    if signal.get("measured_at") and _timestamp(signal["measured_at"]) > _timestamp(
        records[0]["recorded_at"]
    ):
        raise EvidenceIntegrityError("signal measurement follows event")
    links["pattern"] = bool(pattern_id)
    links["proposal"] = _hash(patch_hash, 64)
    outcomes = [r["payload"] for r in records if r["kind"] == "outcome"]
    latest = outcomes[-1] if outcomes else {}
    bound = (
        bool(pattern_id and patch_hash)
        and latest.get("pattern_id") == pattern_id
        and latest.get("patch_hash") == patch_hash
    )
    measured = bound and verified_measurement(latest, verifier, allow_synthetic=allow_synthetic)
    scope = (
        "synthetic"
        if measured and latest.get("synthetic") is True
        else ("verified" if measured else "unknown")
    )
    merge_sha = latest.get("merged_sha")
    key = EvidenceStore.observation_key(latest) if latest else ""
    observations: set[str] = set()
    observed_payloads: dict[str, Mapping[str, Any]] = {}
    consumption: dict[str, str] = {}
    qualifications: set[str] = set()
    for record in records:
        payload = record["payload"]
        if record["kind"] == "outcome":
            observation = EvidenceStore.observation_key(payload)
            if observation in observations:
                raise EvidenceIntegrityError("duplicate outcome observation")
            observations.add(observation)
            observed_payloads[observation] = payload
        elif record["kind"] == "consumption":
            observation, state = payload["observation_key"], payload["state"]
            if observation not in observations or (
                (state == "pending" and observation in consumption)
                or (state == "complete" and consumption.get(observation) != "pending")
            ):
                raise EvidenceIntegrityError("invalid consumption chain")
            consumption[observation] = state
        elif record["kind"] == "qualification":
            observation = payload["observation_key"]
            original = observed_payloads.get(observation)
            if (
                original is None
                or consumption.get(observation) != "complete"
                or observation in qualifications
                or payload["observation_hash"] != EvidenceStore._observation_hash(original)
                or payload["mode"]
                != ("synthetic" if original.get("synthetic") is True else "production")
                or any(
                    payload[field] != original.get(field)
                    for field in ("event_id", "pattern_id", "patch_hash", "merged_sha", "outcome")
                )
            ):
                raise EvidenceIntegrityError("invalid durable qualification chain")
            qualifications.add(observation)
    consumed = consumption.get(key) == "complete"
    executions = [(index, r) for index, r in enumerate(records) if r["kind"] == "execution"]
    prs = [(index, r) for index, r in enumerate(records) if r["kind"] == "pr"]
    measurements = [(index, r) for index, r in enumerate(records) if r["kind"] == "outcome"]
    confidences = [(index, r) for index, r in enumerate(records) if r["kind"] == "confidence"]
    chain = [group[-1] for group in (executions, prs, measurements, confidences) if group]
    if any(before[0] >= after[0] for before, after in zip(chain, chain[1:])):
        raise EvidenceIntegrityError("event execution PR measurement confidence order invalid")
    execution = executions[-1][1]["payload"] if executions else {}
    attempt_id = execution.get("attempt_id")
    candidate_tree_hash = execution.get("candidate_tree_hash")
    if candidate_tree_hash is not None and not _hash(candidate_tree_hash, 40):
        raise EvidenceIntegrityError("invalid candidate tree identity")
    base_sha = event.get("sha")
    for record in records:
        kind = record.get("kind")
        payload = record.get("payload", {})
        for name, expected in (
            ("event_id", event_id),
            ("pattern_id", pattern_id),
            ("patch_hash", patch_hash),
            ("merged_sha", merge_sha),
            ("source_sha", event.get("sha")),
            ("base_sha", event.get("sha")),
            ("repo", event.get("repo")),
            ("attempt_id", attempt_id),
            ("candidate_tree_hash", candidate_tree_hash),
        ):
            identity = _identity(payload, name)
            if identity is not None and expected and identity != expected:
                raise EvidenceIntegrityError(f"mismatched {name}")
        if kind == "execution":
            for gate in (payload.get("baseline_gate_logs") or []) + (
                payload.get("gate_logs") or []
            ):
                if not isinstance(gate, Mapping):
                    continue
                started_at = gate.get("started_at")
                finished_at = gate.get("finished_at")
                if started_at is not None or finished_at is not None:
                    start, finish = _timestamp(started_at), _timestamp(finished_at)
                    if not (
                        _timestamp(records[0]["recorded_at"])
                        <= start
                        <= finish
                        <= _timestamp(record["recorded_at"])
                    ):
                        raise EvidenceIntegrityError("gate execution chronology invalid")
            links["gates"] = (
                payload.get("status") == "verified"
                and payload.get("patch_hash") == patch_hash
                and _hash(patch_hash, 64)
                and _hash(payload.get("base_sha"), 40)
                and payload.get("base_sha") == base_sha
                and isinstance(payload.get("attempt_id"), str)
                and bool(payload["attempt_id"].strip())
                and _passing_gates(payload, proposal)
                and _authorized_regression(payload, proposal)
            )
        elif kind == "pr":
            links["pr"] = (
                payload.get("merge_state") in ("merged", "reverted")
                and type(payload.get("pr_number")) is int
                and payload["pr_number"] > 0
                and payload.get("patch_hash") == patch_hash
                and _hash(merge_sha, 40)
                and payload.get("merged_sha") == merge_sha
                and _identity(payload, "attempt_id") == attempt_id
                and _identity(payload, "base_sha") == base_sha
                and bool(payload.get("merged_at"))
            )
            if payload.get("merged_at"):
                merged_at = _timestamp(payload["merged_at"])
                if (
                    executions and merged_at < _timestamp(executions[-1][1]["recorded_at"])
                ) or merged_at > _timestamp(record["recorded_at"]):
                    raise EvidenceIntegrityError("merge timestamp outside execution/PR chronology")
        elif kind == "outcome":
            if payload is latest:
                provenance = payload.get("provenance") or {}
                measured = bool(
                    measured
                    and _hash(merge_sha, 40)
                    and _identity(payload, "attempt_id") == attempt_id
                    and _identity(payload, "base_sha") == base_sha
                    and provenance.get("measured_at")
                )
                if provenance.get("measured_at"):
                    measured_at = _timestamp(provenance["measured_at"])
                    if (
                        prs
                        and prs[-1][1]["payload"].get("merged_at")
                        and measured_at < _timestamp(prs[-1][1]["payload"]["merged_at"])
                    ) or measured_at > _timestamp(record["recorded_at"]):
                        raise EvidenceIntegrityError("post-merge measurement chronology invalid")
        elif kind == "confidence":
            links["confidence_update"] = (
                consumed
                and key in qualifications
                and measured
                and payload.get("pattern_id") == pattern_id
                and payload.get("patch_hash") == patch_hash
                and payload.get("observation_key") == key
                and payload.get("outcome") == latest.get("outcome")
                and _identity(payload, "attempt_id") == attempt_id
                and _identity(payload, "base_sha") == base_sha
                and payload.get("merged_sha") == merge_sha
                and type(payload.get("new_rate")) in (int, float)
                and 0 <= payload["new_rate"] <= 1
            )
    links["post_merge_measurement"] = bool(measured)
    if not measured:
        scope = "unknown"
    return links, scope


def evaluate_event(
    store: Any,
    event_id: str,
    *,
    measurement_verifier: Optional[Callable[[Mapping[str, Any]], bool]] = None,
    allow_synthetic: bool = False,
) -> EvaluationReport:
    """Evaluate chronologically bound declared gates; read-only, never raises.

    ``allow_synthetic`` is an explicit offline-fixture opt-in, not production
    evidence. A complete simulation remains labelled ``proof_scope=synthetic``.
    """

    try:
        records = store.audit_trail(event_id)
    except Exception as e:  # noqa: BLE001 - evaluator must not crash the loop
        logger.error("Failed to read audit trail for %s: %s", event_id, e)
        return EvaluationReport(event_id=event_id, verdict=UNVERIFIED, evidence_count=0)

    if not records:
        return EvaluationReport(event_id=event_id, verdict=UNVERIFIED, evidence_count=0)

    try:
        links, scope = _classify(records, event_id, measurement_verifier, allow_synthetic)
    except Exception as exc:  # noqa: BLE001
        logger.error("Invalid evidence for %s: %s", event_id, exc)
        return EvaluationReport(
            event_id=event_id,
            verdict=UNVERIFIED,
            evidence_count=len(records),
            links={link: False for link in _REQUIRED_LINKS},
            missing=_REQUIRED_LINKS,
        )
    missing = tuple(link for link in _REQUIRED_LINKS if not links[link])
    verdict = COMPLETE if not missing else PARTIAL
    return EvaluationReport(
        event_id=event_id,
        verdict=verdict,
        links=links,
        missing=missing,
        evidence_count=len(records),
        proof_scope=scope,
    )


def evaluate_store(
    store: Any,
    *,
    measurement_verifier: Optional[Callable[[Mapping[str, Any]], bool]] = None,
    allow_synthetic: bool = False,
) -> List[EvaluationReport]:
    """Evaluate every recorded event. Read-only."""

    try:
        records = store.audit_trail()
        for record in records:
            EvidenceStore._validate_record(record)
        event_ids = [r["payload"]["event_id"] for r in records if r["kind"] == "event"]
    except Exception as exc:  # noqa: BLE001
        logger.error("Invalid store evidence: %s", exc)
        return [EvaluationReport(event_id="", verdict=UNVERIFIED)]
    return [
        evaluate_event(
            store, eid, measurement_verifier=measurement_verifier, allow_synthetic=allow_synthetic
        )
        for eid in dict.fromkeys(event_ids)
    ]
