"""Separate read-only joins for post-attempt scanner and calibration handoff.

No live transport is implemented: a callable's advertised timeout cannot enforce
a hard deadline. Recorded fixtures are bounded local bytes, never fresh GitHub
evidence. A persisted PR binding is required before associating scanner metadata
with an attempt; even that association is not causal or learning evidence.
A final journal digest recheck detects intervening local writes, not an atomic
snapshot or a guarantee against changes after the recheck.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Mapping

from codex.cognitive_brain.evidence_store import EvidenceIntegrityError, EvidenceStore
from codex.cognitive_brain.merged_observation import observe_merged_pr
from codex.cognitive_brain.pattern_calibration import calibrate_pattern

_MAX_RESPONSE_BYTES = 256 * 1024
_MAX_FIXTURE_BYTES = 1024 * 1024
_CONTEXT_KEYS = frozenset(
    {
        "repo",
        "pr_number",
        "expected_sha",
        "base_ref",
        "run_id",
        "run_attempt",
        "workflow_name",
        "event",
        "window_start",
        "window_end",
        "observed_at",
        "max_age",
        "evidence_origin",
    }
)


class RecordedFixtureReader:
    """Fixed-origin, nine-read, 60-second, bounded-byte offline fixture reader.

    Values are UTF-8 JSON bytes, not callbacks or file handles. No credentials,
    environment discovery, redirects, headers, sockets or network are involved.
    ``source_id`` is a nonsecret fixture identifier, never an authorization claim.
    """

    def __init__(
        self,
        responses: Mapping[str, tuple[int, bytes]],
        *,
        repo: str,
        source_id: str,
        evidence_origin: str = "recorded",
    ) -> None:
        if (
            not isinstance(repo, str)
            or re.fullmatch(r"[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+", repo) is None
            or repo.split("/")[1] in (".", "..")
            or not isinstance(source_id, str)
            or re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", source_id) is None
            or evidence_origin not in ("recorded", "synthetic")
            or len(responses) > 9
        ):
            raise ValueError("invalid recorded fixture context")
        self._repo = repo
        self._source_id = source_id
        self._evidence_origin = evidence_origin
        self._responses: dict[str, tuple[int, bytes]] = {}
        total = 0
        prefix = rf"/repos/{re.escape(repo)}/"
        suffix = r"(?:pulls/[1-9][0-9]*|actions/runs/[1-9][0-9]*(?:/attempts/[1-9][0-9]*/jobs\?per_page=100&page=[1-9][0-9]*)?)"
        for path, response in responses.items():
            status, body = response
            if (
                not isinstance(path, str)
                or re.fullmatch(prefix + suffix, path) is None
                or type(status) is not int
                or type(body) is not bytes
                or len(body) > _MAX_RESPONSE_BYTES
            ):
                raise ValueError("invalid or oversized recorded response")
            total += len(body)
            if total > _MAX_FIXTURE_BYTES:
                raise ValueError("recorded fixture exceeds byte budget")
            self._responses[path] = (status, body)
        self._deadline = time.monotonic() + 60
        self._reads = 0

    @property
    def repo(self) -> str:
        return self._repo

    @property
    def source_id(self) -> str:
        return self._source_id

    @property
    def evidence_origin(self) -> str:
        return self._evidence_origin

    def __call__(self, path: str) -> tuple[int, Any]:
        self._reads += 1
        if self._reads > 9 or time.monotonic() >= self._deadline:
            raise ValueError("recorded reader budget exhausted")
        status, body = self._responses[path]
        if type(body) is not bytes or len(body) > _MAX_RESPONSE_BYTES:
            raise ValueError("recorded response exceeds byte budget")
        payload = json.loads(body)
        if time.monotonic() >= self._deadline:
            raise ValueError("recorded reader deadline exceeded")
        return status, payload


def _identity(payload: Mapping[str, Any], name: str) -> Any:
    details = payload.get("details") or {}
    if not isinstance(details, Mapping):
        raise EvidenceIntegrityError("malformed identity details")
    if name in payload and name in details and payload[name] != details[name]:
        raise EvidenceIntegrityError(f"contradictory {name}")
    return payload.get(name, details.get(name))


def _jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def compose_post_attempt_handoff(
    store: EvidenceStore,
    *,
    event_id: str,
    pattern_id: str | None = None,
    patch_hash: str | None = None,
    attempt_id: str | None = None,
    observation_context: Mapping[str, Any] | None = None,
    reader: RecordedFixtureReader | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Join durable identities without executing, consuming, recovering or learning.

    Missing links yield partial/unavailable reasons. Contradictions reject the
    join rather than choosing a convenient terminal or guessing an association.
    Only allowlisted source metadata is returned, never full persisted payloads.
    """
    current = now if now is not None else datetime.now(timezone.utc)
    if not isinstance(store, EvidenceStore):
        raise TypeError("handoff requires an EvidenceStore")
    if not isinstance(event_id, str) or not event_id or current.utcoffset() is None:
        raise ValueError("event identity and aware handoff time required")
    requested_origin = (observation_context or {}).get("evidence_origin", "unknown")
    origin = (
        requested_origin if requested_origin in ("live", "recorded", "synthetic") else "unknown"
    )
    result: dict[str, Any] = {
        "stage": "post-attempt-read-only",
        "status": "partial",
        "reasons": [],
        "identity": {"event_id": event_id},
        "sources": [],
        "observation": {
            "availability": "unavailable",
            "reason": "no supported bounded live transport; recorded reader required",
            "evidence_origin": origin,
            "origin_authenticated": False,
            "scope": "compliance-scanners",
            "learning_eligible": False,
        },
        "calibration": {"availability": "unavailable", "diagnostic_only": True},
        "execution_authorized": False,
        "integration_authorized": False,
        "learning_performed": False,
        "learning_eligible": False,
        "recovery_performed": False,
        "causal_evidence": False,
        "human_handoff_required": True,
    }
    try:
        # Reconstruct persisted bytes; caller-mutated cached records are not proof.
        snapshot = EvidenceStore(store.path, allow_synthetic=store.allow_synthetic)
        records = snapshot.audit_trail(event_id)
        initial_digest = snapshot._journal_sha256
        result["snapshot"] = {
            "journal_sha256": initial_digest,
            "atomic": False,
            "unchanged_on_recheck": None,
        }
        events = [r["payload"] for r in records if r["kind"] == "event"]
        if len(events) != 1:
            result["reasons"].append("unique persisted event unavailable")
            return result
        event = events[0]
        pattern, proposal = event.get("pattern") or {}, event.get("proposal") or {}
        exact = {
            "event_id": event_id,
            "pattern_id": pattern.get("pattern_id"),
            "patch_hash": proposal.get("patch_hash"),
            "repo": event.get("repo"),
            "base_sha": event.get("sha"),
        }
        for name, expected in (("pattern_id", pattern_id), ("patch_hash", patch_hash)):
            if expected is not None and exact[name] != expected:
                raise EvidenceIntegrityError(f"mismatched {name}")
        if not exact["pattern_id"] or not exact["patch_hash"]:
            result["reasons"].append("persisted pattern/proposal identity unavailable")
            return result
        if (
            not isinstance(exact["pattern_id"], str)
            or re.fullmatch(r"[0-9a-f]{64}", exact["patch_hash"]) is None
            or not isinstance(exact["base_sha"], str)
            or re.fullmatch(r"[0-9a-f]{40}", exact["base_sha"]) is None
        ):
            raise EvidenceIntegrityError("invalid persisted proposal identity")
        executions = [r["payload"] for r in records if r["kind"] == "execution"]
        if executions:
            if any(payload != executions[0] for payload in executions[1:]):
                raise EvidenceIntegrityError("contradictory execution terminals")
            execution = executions[0]
            exact["attempt_id"] = execution.get("attempt_id")
            exact["execution_status"] = execution.get("status")
        else:
            exact["attempt_id"] = None
            result["reasons"].append("persisted execution unavailable")
        if attempt_id is not None and exact["attempt_id"] != attempt_id:
            raise EvidenceIntegrityError("mismatched attempt_id")
        for payload in [proposal] + executions:
            for name in ("event_id", "pattern_id", "patch_hash", "base_sha", "attempt_id"):
                actual = _identity(payload, name)
                if actual is not None and exact.get(name) is not None and actual != exact[name]:
                    raise EvidenceIntegrityError(f"mismatched proposal/execution {name}")
            for gate in (payload.get("gate_logs") or []) + (
                payload.get("baseline_gate_logs") or []
            ):
                if not isinstance(gate, Mapping):
                    raise EvidenceIntegrityError("malformed gate identity")
                for name in ("event_id", "pattern_id", "patch_hash", "base_sha", "attempt_id"):
                    if name in gate and gate[name] != exact.get(name):
                        raise EvidenceIntegrityError(f"mismatched gate {name}")
        if exact["attempt_id"] is None:
            result["reasons"].append("persisted execution attempt identity unavailable")
        prs = [r["payload"] for r in records if r["kind"] == "pr"]
        if prs:
            for name in ("merged_sha", "pr_number", "merge_state"):
                if any(_identity(p, name) != _identity(prs[0], name) for p in prs[1:]):
                    raise EvidenceIntegrityError(f"contradictory PR {name}")
            exact["merged_sha"] = _identity(prs[0], "merged_sha")
        for record in records:
            payload = record["payload"]
            provenance = payload.get("provenance") or {}
            if not isinstance(provenance, Mapping):
                raise EvidenceIntegrityError("malformed source metadata")
            for name in (
                "event_id",
                "pattern_id",
                "patch_hash",
                "repo",
                "base_sha",
                "attempt_id",
                "merged_sha",
            ):
                actual = _identity(payload, name)
                if actual is not None and exact.get(name) is not None and actual != exact[name]:
                    raise EvidenceIntegrityError(f"mismatched {name}")
            result["sources"].append(
                {
                    "kind": record["kind"],
                    "recorded_at": record["recorded_at"],
                    "event_id": payload["event_id"],
                    "observation_id": payload.get("observation_id"),
                    "source": provenance.get("source"),
                    "measured_at": provenance.get("measured_at"),
                }
            )
        result["identity"] = exact
        signal = event.get("signal") or {}
        result["signal_source"] = {
            "source": signal.get("source"),
            "measured_at": signal.get("measured_at"),
            "availability": signal.get("availability"),
            "synthetic": event.get("synthetic", False),
        }
        calibration = calibrate_pattern(snapshot, exact["pattern_id"], now=current)
        result["calibration"] = {"availability": "available", **_jsonable(asdict(calibration))}
        breaker = snapshot._breakers.get(exact["pattern_id"])
        result["calibration"]["eligibility"] = (
            "disabled"
            if breaker is not None and breaker.disabled
            else (
                "unknown"
                if snapshot.allow_synthetic or exact["pattern_id"] in snapshot._unknown_patterns
                else "receipt-qualified-history-only"
            )
        )
        if calibration.state != "calibrated":
            result["reasons"].append(f"calibration: {calibration.state}: {calibration.reason}")
        context = dict(observation_context or {})
        if context:
            if set(context) != _CONTEXT_KEYS:
                raise EvidenceIntegrityError("invalid observation context fields")
            if context["repo"] != exact["repo"]:
                raise EvidenceIntegrityError("mismatched observation repo")
            if context["observed_at"] != current:
                raise EvidenceIntegrityError("mismatched observation assessment time")
            if prs:
                for name, key in (
                    ("merged_sha", "expected_sha"),
                    ("pr_number", "pr_number"),
                    ("base_ref", "base_ref"),
                    ("run_id", "run_id"),
                    ("run_attempt", "run_attempt"),
                    ("workflow_name", "workflow_name"),
                    ("event", "event"),
                    ("window_start", "window_start"),
                    ("window_end", "window_end"),
                ):
                    for record in records:
                        payload = record["payload"]
                        persisted = _identity(payload, name)
                        if persisted is not None and _jsonable(context[key]) != persisted:
                            raise EvidenceIntegrityError(f"mismatched observation {name}")
            if (
                not prs
                or prs[0].get("merge_state") != "merged"
                or not exact.get("merged_sha")
                or exact["attempt_id"] is None
                or exact.get("execution_status") != "verified"
                or any(
                    _identity(prs[0], name) != exact[name]
                    for name in ("attempt_id", "patch_hash", "base_sha")
                )
            ):
                result["observation"]["reason"] = "persisted attempt-bound merged PR unavailable"
            elif type(reader) is not RecordedFixtureReader:
                result["observation"]["reason"] = "no supported bounded live transport"
            elif (
                reader.repo != context["repo"]
                or reader.evidence_origin != context["evidence_origin"]
            ):
                raise EvidenceIntegrityError("mismatched reader origin/repository")
            else:
                observation = observe_merged_pr(reader=reader, **context)
                if observation.availability == "measured":
                    for payload in prs:
                        persisted_merge = _identity(payload, "merged_at")
                        if persisted_merge is not None and persisted_merge != observation.merged_at:
                            raise EvidenceIntegrityError("mismatched observed merge timestamp")
                result["observation"] = observation.to_dict()
                result["observation"]["source_id"] = reader.source_id
                result["observation"]["origin_authenticated"] = False
                result["observation"]["fresh_live_evidence"] = False
        if result["observation"]["availability"] != "measured":
            result["reasons"].append(result["observation"]["reason"])
        final_digest = EvidenceStore(store.path)._journal_sha256
        result["snapshot"]["unchanged_on_recheck"] = final_digest == initial_digest
        if final_digest != initial_digest:
            result["reasons"].append("journal changed during non-atomic handoff collection")
            result["calibration"] = {
                "availability": "unavailable",
                "reason": "journal changed during collection",
                "diagnostic_only": True,
            }
            result["observation"] = {
                "availability": "unavailable",
                "reason": "journal changed during collection",
                "evidence_origin": origin,
                "origin_authenticated": False,
                "scope": "compliance-scanners",
                "learning_eligible": False,
            }
        if not result["reasons"]:
            result["status"] = "joined"
        return result
    except (EvidenceIntegrityError, OSError, ValueError, TypeError, KeyError):
        # Never echo persisted remote text, credentials, headers or exception text.
        result["status"] = "rejected"
        result["reasons"] = ["persisted or requested evidence identities conflict or are invalid"]
        result["observation"] = {
            "availability": "unavailable",
            "reason": "join rejected",
            "evidence_origin": origin,
            "origin_authenticated": False,
            "scope": "compliance-scanners",
            "learning_eligible": False,
        }
        return result
