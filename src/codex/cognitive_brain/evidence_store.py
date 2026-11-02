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

import fcntl
import hashlib
import json
import logging
import os
import re
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Mapping, Optional

from codex.cognitive_brain.learning_reconciliation import (
    DecisionVerifier,
    ExternalSnapshot,
    LearningRecovery,
    SnapshotReader,
)

logger = logging.getLogger(__name__)

EVIDENCE_STORE_SCHEMA_VERSION = "1.0.0"
DEFAULT_STORE_PATH = Path(".codex") / "improvement" / "evidence.jsonl"

# Circuit-breaker defaults.
DEFAULT_MAX_CONSECUTIVE_FAILURES = 3
DEFAULT_STALE_AFTER_DAYS = 90


class EvidenceIntegrityError(ValueError):
    """Invalid durable evidence; the original file is never repaired implicitly."""


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
                self._disable_reason = f"{self._consecutive_failures} consecutive failing outcomes"

    def check_stale(self, last_used_iso: str) -> bool:
        """Disable when the pattern has been idle beyond the staleness window."""
        try:
            last = datetime.fromisoformat(last_used_iso.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return False
        if last.tzinfo is None:
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
    """Durable audit store with verifier-qualified production circuit breakers.

    ``allow_synthetic=True`` selects an isolated offline-fixture breaker history:
    only synthetic observations affect it. Default production mode ignores all
    synthetic and unverified observations, including success/reset signals.
    Production qualification receipts are written only after verifier-qualified
    consumption completes. They reconstruct local eligibility without ambient
    credentials. Raw measured history without such receipts is unknown and
    blocks eligibility; a caller merged/verified boolean never becomes proof.
    Receipts assume a trusted local journal, not cryptographic protection from
    an actor who can arbitrarily rewrite the evidence file.
    """

    path: Path = DEFAULT_STORE_PATH
    measurement_verifier: Optional[Callable[[Mapping[str, Any]], bool]] = None
    allow_synthetic: bool = False
    _records: List[Dict[str, Any]] = field(default_factory=list)
    _event_ids: set = field(default_factory=set)
    _outcomes: Dict[str, Mapping[str, Any]] = field(default_factory=dict)
    _breakers: Dict[str, CircuitBreaker] = field(default_factory=dict)
    _pattern_events: Dict[str, set[str]] = field(default_factory=dict)
    _observations: Dict[str, Mapping[str, Any]] = field(default_factory=dict)
    _consumption: Dict[str, str] = field(default_factory=dict)
    _qualifications: Dict[str, str] = field(default_factory=dict)
    _unknown_patterns: set[str] = field(default_factory=set)
    _reconciliations: Dict[str, Mapping[str, Any]] = field(default_factory=dict)
    _journal_sha256: str = ""

    def __post_init__(self) -> None:
        if type(self.allow_synthetic) is not bool:
            raise EvidenceIntegrityError("fixture mode must be an explicit boolean")
        self.path = Path(self.path)
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        self._records.clear()
        self._event_ids.clear()
        self._outcomes.clear()
        self._breakers.clear()
        self._pattern_events.clear()
        self._observations.clear()
        self._consumption.clear()
        self._qualifications.clear()
        self._unknown_patterns.clear()
        self._reconciliations.clear()
        self._journal_sha256 = hashlib.sha256(b"").hexdigest()
        if not self.path.exists():
            return
        with open(self.path, "rb") as handle:
            fcntl.flock(handle, fcntl.LOCK_SH)
            try:
                contents = handle.read()
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)
        self._journal_sha256 = hashlib.sha256(contents).hexdigest()
        if contents and not contents.endswith(b"\n"):
            raise EvidenceIntegrityError("unterminated evidence tail; original bytes preserved")
        try:
            lines = contents.decode("utf-8").splitlines(keepends=True)
        except UnicodeError as exc:
            raise EvidenceIntegrityError(
                "invalid evidence encoding; original bytes preserved"
            ) from exc
        prefix = hashlib.sha256()
        for number, line in enumerate(lines, 1):
            previous_digest = prefix.hexdigest()
            prefix.update(line.encode("utf-8"))
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                self._validate_record(record)
            except (ValueError, TypeError, KeyError, AttributeError) as exc:
                raise EvidenceIntegrityError(f"invalid evidence record at line {number}") from exc
            self._records.append(record)
            if record.get("kind") == "event":
                event_id = record["payload"]["event_id"]
                if event_id in self._event_ids:
                    raise EvidenceIntegrityError(f"duplicate event at line {number}")
                self._event_ids.add(event_id)
            elif record.get("kind") == "outcome":
                payload = record["payload"]
                self._outcomes[payload["event_id"]] = payload
                pat = payload.get("pattern_id")
                if pat:
                    self._pattern_events.setdefault(pat, set()).add(payload["event_id"])
                    if (
                        self.allow_synthetic
                        and payload.get("synthetic") is True
                        and payload.get("merged") is True
                        and payload.get("outcome") in ("success", "regression", "rollback")
                    ):
                        self.breaker(pat).record(payload["outcome"])
                key = self.observation_key(payload)
                if key in self._observations:
                    raise EvidenceIntegrityError(f"duplicate observation at line {number}")
                self._observations[key] = payload
            elif record["kind"] == "consumption":
                payload = record["payload"]
                key, state = payload["observation_key"], payload["state"]
                previous = self._consumption.get(key)
                if (
                    key not in self._observations
                    or payload["event_id"] != self._observations[key]["event_id"]
                    or (
                        (state == "pending" and previous is not None)
                        or (state == "complete" and previous != "pending")
                    )
                ):
                    raise EvidenceIntegrityError(f"invalid consumption at line {number}")
                self._consumption[key] = state
            elif record["kind"] == "qualification":
                self._accept_qualification(record["payload"])
            elif record["kind"] == "learning_reconciliation":
                payload = record["payload"]
                identity = payload["identity"]
                key = identity["observation_key"]
                if (
                    key not in self._observations
                    or key in self._qualifications
                    or key in self._reconciliations
                    or identity["journal_sha256"] != previous_digest
                    or payload["event_id"] != self._observations[key]["event_id"]
                    or self._consumption.get(key) not in ("pending", "complete")
                    or identity
                    != self._learning_identity(
                        key, identity["external_snapshot"], identity["journal_sha256"]
                    ).as_dict()
                ):
                    raise EvidenceIntegrityError(f"invalid reconciliation at line {number}")
                self._reconciliations[key] = payload
                if payload["disposition"] == "already_applied":
                    self._consumption[key] = "complete"
                    self._accept_qualification(payload["qualification"])
                else:
                    self._consumption[key] = "abandoned"
        events = {
            r["payload"]["event_id"]: r["payload"] for r in self._records if r["kind"] == "event"
        }
        identities: dict[str, dict[str, str]] = {}
        for record in self._records:
            if record["kind"] != "outcome":
                continue
            payload = record["payload"]
            event = events.get(payload["event_id"], {})
            expected = identities.setdefault(payload["event_id"], {})
            for name, source in (
                ("pattern_id", (event.get("pattern") or {}).get("pattern_id")),
                ("patch_hash", (event.get("proposal") or {}).get("patch_hash")),
                ("merged_sha", None),
            ):
                value = payload.get(name)
                if (source and value != source) or (expected.get(name) and value != expected[name]):
                    raise EvidenceIntegrityError(f"inconsistent durable outcome {name}")
                if value:
                    expected[name] = value
        if not self.allow_synthetic:
            for key, payload in self._observations.items():
                if self._qualifications.get(key) == "production":
                    self.breaker(payload["pattern_id"]).record(payload["outcome"])
                    continue
                if (
                    payload.get("synthetic") is not True
                    and payload.get("merged") is True
                    and payload.get("outcome") in ("success", "regression", "rollback")
                    and payload.get("pattern_id")
                    and self._qualifications.get(key) != "production"
                ):
                    self._unknown_patterns.add(payload["pattern_id"])

    def _accept_qualification(self, payload: Mapping[str, Any]) -> None:
        key = payload["observation_key"]
        observation = self._observations.get(key)
        if (
            observation is None
            or self._consumption.get(key) != "complete"
            or key in self._qualifications
            or observation["merged"] is not True
            or dict(payload) != self._qualification_payload(observation)
        ):
            raise EvidenceIntegrityError("invalid qualification identity or ordering")
        self._qualifications[key] = payload["mode"]

    def _qualification_payload(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "event_id": payload["event_id"],
            "observation_key": self.observation_key(payload),
            "proof_kind": "trusted_measurement_consumption",
            "mode": "synthetic" if payload.get("synthetic") is True else "production",
            "pattern_id": payload.get("pattern_id"),
            "patch_hash": payload.get("patch_hash"),
            "merged_sha": payload.get("merged_sha"),
            "outcome": payload["outcome"],
            "observation_hash": self._observation_hash(payload),
        }

    def _qualified_observation(
        self,
        payload: Mapping[str, Any],
        verifier: Optional[Callable[[Mapping[str, Any]], bool]],
    ) -> bool:
        # Local import avoids a module-initialization cycle with the tracker.
        from codex.cognitive_brain.outcome_tracking import verified_measurement

        if not isinstance(payload.get("pattern_id"), str) or not payload["pattern_id"]:
            return False
        if self.allow_synthetic:
            return payload.get("synthetic") is True and verified_measurement(
                payload, allow_synthetic=True
            )
        if payload.get("synthetic") is True:
            return False
        return verified_measurement(deepcopy(payload), verifier or self.measurement_verifier)

    @staticmethod
    def _observation_hash(payload: Mapping[str, Any]) -> str:
        encoded = json.dumps(dict(payload), sort_keys=True, separators=(",", ":"), allow_nan=False)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    @staticmethod
    def _validate_record(record: Any) -> None:
        if (
            not isinstance(record, dict)
            or record.get("schema_version") != EVIDENCE_STORE_SCHEMA_VERSION
        ):
            raise EvidenceIntegrityError("unsupported evidence schema")
        if not isinstance(record.get("kind"), str) or not record["kind"]:
            raise EvidenceIntegrityError("invalid evidence kind")
        timestamp = datetime.fromisoformat(record["recorded_at"].replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            raise EvidenceIntegrityError("record timestamp must be timezone aware")
        payload = record["payload"]
        if (
            not isinstance(payload, dict)
            or not isinstance(payload.get("event_id"), str)
            or not payload["event_id"]
        ):
            raise EvidenceIntegrityError("invalid event identity")
        if record["kind"] == "event":
            for name in ("signal", "pattern", "proposal"):
                if (
                    name in payload
                    and payload[name] is not None
                    and not isinstance(payload[name], dict)
                ):
                    raise EvidenceIntegrityError(f"invalid event {name}")
            for section, names in (
                ("signal", ("source", "measured_at")),
                ("pattern", ("pattern_id",)),
                ("proposal", ("patch_hash",)),
            ):
                body = payload.get(section) or {}
                for name in names:
                    if name in body and (not isinstance(body[name], str) or not body[name]):
                        raise EvidenceIntegrityError(f"invalid event {section}.{name}")
            measured_at = (payload.get("signal") or {}).get("measured_at")
            if measured_at:
                measured = datetime.fromisoformat(measured_at.replace("Z", "+00:00"))
                if measured.tzinfo is None:
                    raise EvidenceIntegrityError("signal timestamp must be timezone aware")
        elif record["kind"] == "outcome":
            if type(payload.get("merged")) is not bool or payload.get("outcome") not in (
                "pending",
                "success",
                "regression",
                "rollback",
            ):
                raise EvidenceIntegrityError("invalid outcome")
            for name in ("pattern_id", "patch_hash", "observation_id", "merged_sha"):
                if payload.get(name) is not None and (
                    not isinstance(payload[name], str) or not payload[name]
                ):
                    raise EvidenceIntegrityError(f"invalid {name}")
            if not isinstance(payload.get("details", {}), dict):
                raise EvidenceIntegrityError("invalid outcome details")
            if not isinstance(payload.get("provenance", {}), dict):
                raise EvidenceIntegrityError("invalid outcome provenance")
            if type(payload.get("synthetic", False)) is not bool:
                raise EvidenceIntegrityError("invalid synthetic marker")
        elif record["kind"] == "consumption":
            if not isinstance(payload.get("observation_key"), str) or payload.get("state") not in (
                "pending",
                "complete",
            ):
                raise EvidenceIntegrityError("invalid consumption record")
        elif record["kind"] == "qualification":
            if (
                not {
                    "event_id",
                    "observation_key",
                    "proof_kind",
                    "mode",
                    "pattern_id",
                    "patch_hash",
                    "merged_sha",
                    "outcome",
                    "observation_hash",
                }.issubset(payload)
                or payload.get("proof_kind") != "trusted_measurement_consumption"
                or payload.get("mode") not in ("production", "synthetic")
                or not isinstance(payload.get("observation_key"), str)
                or not isinstance(payload.get("pattern_id"), str)
                or not payload["pattern_id"]
                or payload.get("outcome") not in ("success", "regression", "rollback")
                or not isinstance(payload.get("observation_hash"), str)
                or re.fullmatch(r"[0-9a-f]{64}", payload["observation_hash"]) is None
            ):
                raise EvidenceIntegrityError("invalid qualification receipt")
            if payload["mode"] == "production" and (
                not isinstance(payload.get("patch_hash"), str)
                or re.fullmatch(r"[0-9a-f]{64}", payload["patch_hash"]) is None
                or not isinstance(payload.get("merged_sha"), str)
                or re.fullmatch(r"[0-9a-f]{40}", payload["merged_sha"]) is None
            ):
                raise EvidenceIntegrityError("invalid production qualification identity")
        elif record["kind"] == "learning_reconciliation":
            identity = payload.get("identity")
            if (
                set(payload) != {"event_id", "identity", "disposition", "qualification"}
                or not isinstance(identity, dict)
                or set(identity) != set(LearningRecovery.__dataclass_fields__)
                or payload.get("disposition") not in ("already_applied", "abandoned")
                or identity.get("state") not in ("pending", "complete")
                or not isinstance(identity.get("external_snapshot"), str)
                or not identity["external_snapshot"]
                or not isinstance(identity.get("attempt_ids"), list)
            ):
                raise EvidenceIntegrityError("invalid learning reconciliation")
            for name in ("observation_key", "event_id", "outcome"):
                if not isinstance(identity.get(name), str) or not identity[name]:
                    raise EvidenceIntegrityError("invalid reconciliation identity")
            for name in (
                "observation_id",
                "pattern_id",
                "patch_hash",
                "merged_sha",
                "attempt_id",
            ):
                if identity[name] is not None and (
                    not isinstance(identity[name], str) or not identity[name]
                ):
                    raise EvidenceIntegrityError("invalid optional reconciliation identity")
            if any(not isinstance(value, str) or not value for value in identity["attempt_ids"]):
                raise EvidenceIntegrityError("invalid reconciliation attempts")
            for name in ("journal_sha256", "observation_hash"):
                if (
                    not isinstance(identity.get(name), str)
                    or re.fullmatch(r"[0-9a-f]{64}", identity[name]) is None
                ):
                    raise EvidenceIntegrityError("invalid reconciliation digest")
            if payload["disposition"] == "abandoned":
                if payload["qualification"] is not None:
                    raise EvidenceIntegrityError("abandonment cannot qualify learning")
            else:
                EvidenceStore._validate_record(
                    {**record, "kind": "qualification", "payload": payload["qualification"]}
                )
        elif record["kind"] == "execution":
            if not isinstance(payload.get("gate_logs", []), list):
                raise EvidenceIntegrityError("invalid gate logs")
            if not isinstance(payload.get("baseline_gate_logs", []), list):
                raise EvidenceIntegrityError("invalid baseline gate logs")
            if (
                "authority" in payload
                and payload["authority"] is not None
                and not isinstance(payload["authority"], dict)
            ):
                raise EvidenceIntegrityError("invalid authority evidence")

    @contextmanager
    def _transaction(self, *, write: bool = True) -> Iterator[None]:
        """Serialize this JSONL's read/check/append only, not external brain writes."""
        lock_path = self.path.with_name(self.path.name + ".lock")
        if write:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        if not write and not lock_path.exists():
            self._load()
            yield
            return
        with open(lock_path, "a" if write else "r", encoding="utf-8") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX if write else fcntl.LOCK_SH)
            try:
                self._load()
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def _append(self, kind: str, payload: Mapping[str, Any]) -> None:
        record = {
            "schema_version": EVIDENCE_STORE_SCHEMA_VERSION,
            "kind": kind,
            "recorded_at": _utcnow(),
            "payload": dict(payload),
        }
        self._validate_record(record)
        encoded = json.dumps(record, allow_nan=False)
        with open(self.path, "a+b") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                handle.seek(0, os.SEEK_END)
                if handle.tell():
                    handle.seek(-1, os.SEEK_END)
                    if handle.read(1) != b"\n":
                        raise EvidenceIntegrityError("unterminated evidence tail; append refused")
                handle.seek(0, os.SEEK_END)
                handle.write((encoded + "\n").encode("utf-8"))
                handle.flush()
                os.fsync(handle.fileno())
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)
        directory = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        self._load()

    # ------------------------------------------------------------------
    # Events and outcomes
    # ------------------------------------------------------------------

    def record_event(self, event_dict: Mapping[str, Any]) -> bool:
        """Persist an event once (idempotent on ``event_id``)."""

        event_id = event_dict.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("event record requires an event_id")
        with self._transaction():
            if event_id in self._event_ids:
                existing = next(
                    r["payload"]
                    for r in self._records
                    if r["kind"] == "event" and r["payload"]["event_id"] == event_id
                )
                if existing != dict(event_dict):
                    raise EvidenceIntegrityError("event identity reused with different evidence")
                return False
            for record in self._records:
                if record["kind"] != "outcome" or record["payload"]["event_id"] != event_id:
                    continue
                for name, expected in (
                    ("pattern_id", (event_dict.get("pattern") or {}).get("pattern_id")),
                    ("patch_hash", (event_dict.get("proposal") or {}).get("patch_hash")),
                ):
                    if expected and record["payload"].get(name) != expected:
                        raise EvidenceIntegrityError(f"event conflicts with persisted {name}")
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
        observation_id: Optional[str] = None,
        merged_sha: Optional[str] = None,
        provenance: Optional[Mapping[str, Any]] = None,
        synthetic: bool = False,
    ) -> None:
        """Persist a measured post-merge outcome for an event.

        Identical measurements are deduplicated, while an explicit transition
        from a pending/unmerged state to a final outcome still updates the
        record. This keeps the outcome store authoritative without discarding
        later measurements for the same event.
        """

        payload = {
            "event_id": event_id,
            "merged": merged,
            "outcome": outcome,
            "pattern_id": pattern_id,
            "patch_hash": patch_hash,
            "details": dict(details or {}),
            "observation_id": observation_id,
            "merged_sha": merged_sha,
            "provenance": dict(provenance or {}),
            "synthetic": synthetic,
        }
        with self._transaction():
            existing = self._outcomes.get(event_id)
            if existing is not None:
                for name in ("pattern_id", "patch_hash", "merged_sha"):
                    if existing.get(name) and payload.get(name) != existing[name]:
                        raise EvidenceIntegrityError(f"outcome {name} does not match event")
            event: Dict[str, Any] = next(
                (
                    r["payload"]
                    for r in self._records
                    if r["kind"] == "event" and r["payload"]["event_id"] == event_id
                ),
                {},
            )
            for name, expected in (
                ("pattern_id", (event.get("pattern") or {}).get("pattern_id")),
                ("patch_hash", (event.get("proposal") or {}).get("patch_hash")),
            ):
                if expected and payload[name] != expected:
                    raise EvidenceIntegrityError(f"outcome {name} does not match event")
            key = self.observation_key(payload)
            if key in self._observations:
                if self._observations[key] != payload:
                    raise EvidenceIntegrityError(
                        "observation identity reused with different evidence"
                    )
                return
            self._append("outcome", payload)

    @staticmethod
    def observation_key(payload: Mapping[str, Any]) -> str:
        """Legacy transitions deduplicate by state; explicit IDs allow later measurements."""
        return json.dumps(
            [
                payload["event_id"],
                payload.get("observation_id") or [payload.get("merged"), payload.get("outcome")],
            ],
            separators=(",", ":"),
        )

    def claim_observation(
        self,
        payload: Mapping[str, Any],
        *,
        measurement_verifier: Optional[Callable[[Mapping[str, Any]], bool]] = None,
    ) -> bool:
        """Write a durable intent. Pending intents require manual reconciliation.

        This guarantees at-most-once invocation, not atomic exactly-once learning
        across the separate brain JSON file. Never retry an ambiguous intent.
        """
        key = self.observation_key(payload)
        with self._transaction():
            if self._observations.get(key) != dict(payload):
                raise EvidenceIntegrityError("observation is not persisted")
            if key in self._consumption:
                if self._consumption[key] == "pending":
                    raise EvidenceIntegrityError("learning pending reconciliation; replay refused")
                return False
            if not self._qualified_observation(payload, measurement_verifier):
                raise EvidenceIntegrityError("unqualified observation cannot be consumed")
            if "pending" in self._consumption.values():
                raise EvidenceIntegrityError("unreconciled learning intent; new learning refused")
            self._append(
                "consumption",
                {"event_id": payload["event_id"], "observation_key": key, "state": "pending"},
            )
            return True

    def complete_observation(
        self,
        payload: Mapping[str, Any],
        *,
        measurement_verifier: Optional[Callable[[Mapping[str, Any]], bool]] = None,
    ) -> None:
        key = self.observation_key(payload)
        with self._transaction():
            if self._consumption.get(key) != "pending":
                raise EvidenceIntegrityError("no pending consumption")
            if self._observations.get(key) != dict(payload) or not self._qualified_observation(
                payload, measurement_verifier
            ):
                raise EvidenceIntegrityError("qualification unconfirmed; learning remains pending")
            self._append(
                "consumption",
                {"event_id": payload["event_id"], "observation_key": key, "state": "complete"},
            )
            self._append(
                "qualification",
                self._qualification_payload(payload),
            )

    def _learning_identity(
        self, key: str, external_snapshot: str, journal_sha256: str
    ) -> LearningRecovery:
        observation = self._observations[key]
        attempts = {
            body["attempt_id"]
            for body in [
                observation.get("provenance", {}),
                *[
                    record["payload"]
                    for record in self._records
                    if record["kind"] in ("event", "execution")
                    and record["payload"]["event_id"] == observation["event_id"]
                    and observation.get("patch_hash")
                    and (
                        record["payload"].get("patch_hash")
                        if record["kind"] == "execution"
                        else (record["payload"].get("proposal") or {}).get("patch_hash")
                    )
                    == observation.get("patch_hash")
                ],
            ]
            if isinstance(body.get("attempt_id"), str) and body["attempt_id"]
        }
        return LearningRecovery(
            observation_key=key,
            observation_id=observation.get("observation_id"),
            event_id=observation["event_id"],
            pattern_id=observation.get("pattern_id"),
            patch_hash=observation.get("patch_hash"),
            merged_sha=observation.get("merged_sha"),
            outcome=observation["outcome"],
            attempt_id=next(iter(attempts)) if len(attempts) == 1 else None,
            attempt_ids=tuple(sorted(attempts)),
            observation_hash=self._observation_hash(observation),
            state=self._consumption[key],
            journal_sha256=journal_sha256,
            external_snapshot=external_snapshot,
        )

    def inspect_learning(self, snapshot_reader: SnapshotReader) -> List[LearningRecovery]:
        """Inspect pending and complete-without-receipt windows without creating files.

        The reader supplies a non-secret consistent external snapshot identity;
        its context must exclude all writers, including non-tracker SDK writers.
        No external data or verifier is inferred from actor flags or digests.
        """
        with snapshot_reader() as snapshot:
            with self._transaction(write=False):
                external_snapshot = self._recheck_external_snapshot(snapshot)
                return [
                    self._learning_identity(key, external_snapshot, self._journal_sha256)
                    for key, state in self._consumption.items()
                    if state in ("pending", "complete") and key not in self._qualifications
                ]

    def reconcile_learning(
        self,
        identity: LearningRecovery,
        disposition: str,
        *,
        snapshot_reader: SnapshotReader,
        policy_verifier: Optional[DecisionVerifier] = None,
        consumption_verifier: Optional[DecisionVerifier] = None,
        measurement_verifier: Optional[Callable[[Mapping[str, Any]], bool]] = None,
        dry_run: bool = True,
    ) -> bool:
        """Resolve without invoking a learner; return False for an identical decision.

        Policy authorization is injected and denied by default. Already-applied
        requires an independent observation-specific consumption receipt as well
        as the existing measurement verifier. Ambiguous writes stay unresolved.
        Dry runs validate identically but never create/append a file or sidecar;
        existing shared read locks are used, not new lock files.
        A single resolving append atomically carries the qualification, if any.
        Execution ledgers are neither read nor changed by this operation.
        """
        if disposition not in ("already_applied", "abandoned") or type(dry_run) is not bool:
            raise EvidenceIntegrityError("invalid reconciliation decision")
        request = {"identity": identity.as_dict(), "disposition": disposition}
        with snapshot_reader() as snapshot:
            # Preflight read-only: denied, missing and stale requests create nothing.
            with self._transaction(write=False):
                self._check_reconciliation(
                    identity,
                    request,
                    snapshot,
                    policy_verifier,
                    consumption_verifier,
                    measurement_verifier,
                )
                previous = self._reconciliations.get(identity.observation_key)
                if previous is not None:
                    return False
                if dry_run:
                    return True
            with self._transaction():
                self._check_reconciliation(
                    identity,
                    request,
                    snapshot,
                    policy_verifier,
                    consumption_verifier,
                    measurement_verifier,
                )
                if identity.observation_key in self._reconciliations:
                    return False
                observation = self._observations[identity.observation_key]
                self._append(
                    "learning_reconciliation",
                    {
                        "event_id": identity.event_id,
                        **request,
                        "qualification": (
                            self._qualification_payload(observation)
                            if disposition == "already_applied"
                            else None
                        ),
                    },
                )
                return True

    def _check_reconciliation(
        self,
        identity: LearningRecovery,
        request: Mapping[str, Any],
        snapshot: ExternalSnapshot,
        policy_verifier: Optional[DecisionVerifier],
        consumption_verifier: Optional[DecisionVerifier],
        measurement_verifier: Optional[Callable[[Mapping[str, Any]], bool]],
    ) -> None:
        external_snapshot = self._recheck_external_snapshot(snapshot)
        if policy_verifier is None or policy_verifier(deepcopy(request)) is not True:
            raise EvidenceIntegrityError("reconciliation denied by trusted policy")
        key = identity.observation_key
        if identity.external_snapshot != external_snapshot or key not in self._observations:
            raise EvidenceIntegrityError("stale or unknown recovery identity")
        previous = self._reconciliations.get(key)
        if previous is not None:
            if (
                previous["identity"] != request["identity"]
                or previous["disposition"] != request["disposition"]
            ):
                raise EvidenceIntegrityError("conflicting reconciliation decision")
            self._recheck_external_snapshot(snapshot)
            return
        if (
            key in self._qualifications
            or self._consumption.get(key) not in ("pending", "complete")
            or identity != self._learning_identity(key, external_snapshot, self._journal_sha256)
        ):
            raise EvidenceIntegrityError("stale or mismatched recovery identity")
        if request["disposition"] == "already_applied" and (
            consumption_verifier is None
            or consumption_verifier(deepcopy(request)) is not True
            or not self._qualified_observation(self._observations[key], measurement_verifier)
        ):
            raise EvidenceIntegrityError("independent consumption and measurement proof required")
        self._recheck_external_snapshot(snapshot)

    @staticmethod
    def _recheck_external_snapshot(snapshot: ExternalSnapshot) -> str:
        if (
            not isinstance(snapshot, ExternalSnapshot)
            or not isinstance(snapshot.identity, str)
            or not snapshot.identity
        ):
            raise EvidenceIntegrityError("readable external snapshot identity required")
        try:
            current = snapshot.recheck()
        except (OSError, ValueError, TypeError) as exc:
            raise EvidenceIntegrityError("external snapshot unavailable") from exc
        if not isinstance(current, str) or current != snapshot.identity:
            raise EvidenceIntegrityError("external snapshot changed")
        return current

    def outcome_for(self, event_id: str) -> Optional[Mapping[str, Any]]:
        """Return the recorded outcome for an event (read-only)."""

        with self._transaction(write=False):
            return deepcopy(self._outcomes.get(event_id))

    def observation_for(self, payload: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
        """Look up the exact observation, never substitute a newer outcome."""
        with self._transaction(write=False):
            return deepcopy(self._observations.get(self.observation_key(payload)))

    def record(self, kind: str, event_id: str, payload: Mapping[str, Any]) -> None:
        """Persist an auxiliary evidence record (execution, pr, confidence).

        These kinds complete the audit trail the evaluator inspects; the
        payload always carries the originating ``event_id`` so the trail
        stays linked end-to-end. Idempotency is enforced on ``event``.
        """

        if not event_id:
            raise ValueError("evidence record requires an event_id")
        if kind in ("event", "outcome", "consumption", "qualification", "learning_reconciliation"):
            raise EvidenceIntegrityError("use the dedicated record API")
        if "event_id" in payload and payload["event_id"] != event_id:
            raise EvidenceIntegrityError("payload cannot override event identity")
        body = {**dict(payload), "event_id": event_id}
        with self._transaction():
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

        with self._transaction(write=False):
            breaker = self.breaker(pattern_id)
        if breaker.disabled:
            return False
        if not self.allow_synthetic and pattern_id in self._unknown_patterns:
            return False
        if last_used_iso and breaker.check_stale(last_used_iso):
            return False
        return not breaker.disabled

    def disable_reason(self, pattern_id: str) -> str:
        if not self.breaker(pattern_id).disabled and pattern_id in self._unknown_patterns:
            return "unknown eligibility: unqualified measured outcome history"
        return self.breaker(pattern_id).reason

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    def audit_trail(self, event_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Read-only view of the recorded evidence, optionally per event."""

        if event_id is None:
            with self._transaction(write=False):
                return deepcopy(self._records)
        with self._transaction(write=False):
            return deepcopy(
                [r for r in self._records if r.get("payload", {}).get("event_id") == event_id]
            )

    def backup(self, destination: Path) -> Path:
        """Copy the store to *destination* (restore by pointing at the copy)."""

        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            with open(self.path, "rb") as handle:
                fcntl.flock(handle, fcntl.LOCK_SH)
                try:
                    destination.write_bytes(handle.read())
                finally:
                    fcntl.flock(handle, fcntl.LOCK_UN)
        else:
            destination.write_text("", encoding="utf-8")
        return destination

    def stats(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "events": len(self._event_ids),
            "outcomes": len(self._outcomes),
            "disabled_patterns": [pid for pid, b in self._breakers.items() if b.disabled],
            "unknown_patterns": sorted(self._unknown_patterns),
        }
