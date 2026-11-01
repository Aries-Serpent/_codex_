"""Outcome measurement and calibrated pattern-confidence updates.

Confidence is updated *only* from an outcome traceable to the original
event (pattern ID + patch hash) and only after the merge produced a
measured post-merge signal. Unverified or pending outcomes never touch
the pattern store.
"""

from __future__ import annotations

import fcntl
import json
import logging
import os
import re
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Optional

from codex.cognitive_brain.evidence_store import EvidenceIntegrityError, EvidenceStore

logger = logging.getLogger(__name__)

# Post-merge outcomes that are strong enough evidence to move confidence.
_MEASURED_OUTCOMES = frozenset({"success", "regression", "rollback"})

_OUTCOME_TO_FEEDBACK = {
    "success": "success",
    "regression": "failure",
    "rollback": "failure",
}


class _StoreOutcomeSource:
    def __init__(self, store: EvidenceStore) -> None:
        self.store = store

    def __call__(self, event_id: str) -> Optional[Mapping[str, Any]]:
        return self.store.outcome_for(event_id)


def verified_measurement(
    record: Mapping[str, Any],
    verifier: Optional[Callable[[Mapping[str, Any]], bool]] = None,
    *,
    allow_synthetic: bool = False,
) -> bool:
    """Synthetic proof is labelled; production requires an external trust seam.

    SHA/provenance strings and a caller's merged boolean are not authentication.
    The injected verifier must verify the merge and measured observation against
    its trusted source; this module performs no hosted verification itself.
    """
    if record.get("merged") is not True or record.get("outcome") not in _MEASURED_OUTCOMES:
        return False
    if record.get("synthetic") is True:
        return allow_synthetic is True
    sha = record.get("merged_sha")
    provenance = record.get("provenance")
    if (
        not isinstance(sha, str)
        or re.fullmatch(r"[0-9a-f]{40}", sha) is None
        or not isinstance(record.get("patch_hash"), str)
        or re.fullmatch(r"[0-9a-f]{64}", record["patch_hash"]) is None
        or not isinstance(record.get("observation_id"), str)
        or not record["observation_id"].strip()
        or not isinstance(provenance, Mapping)
        or not isinstance(provenance.get("source"), str)
        or not provenance["source"].strip()
        or not provenance.get("measured_at")
        or verifier is None
    ):
        return False
    try:
        measured_at = datetime.fromisoformat(provenance["measured_at"].replace("Z", "+00:00"))
        if measured_at.tzinfo is None:
            return False
    except (AttributeError, TypeError, ValueError):
        return False
    return verifier(record) is True


def store_outcome_source(store: Any) -> Callable[[str], Optional[Mapping[str, Any]]]:
    """Adapt an :class:`EvidenceStore` into an OutcomeTracker outcome source.

    The returned callable reads the recorded post-merge outcome for an
    event ID from the store, so ``OutcomeTracker`` consumes only outcomes
    that were actually persisted (the verified-outcome seam).
    """

    return _StoreOutcomeSource(store)


@dataclass(frozen=True, slots=True)
class ConfidenceUpdate:
    """Traceable record of a confidence change."""

    pattern_id: str
    event_id: str
    patch_hash: str
    outcome: str
    previous_rate: float
    new_rate: float
    alpha: float
    observation_key: str = ""
    synthetic: bool = False


class OutcomeTracker:
    """Link verified post-merge outcomes to pattern-confidence updates.

    Parameters
    ----------
    brain_interface:
        The agent brain interface exposing ``submit_learning`` and the
        pattern store (the existing EMA seam).
    outcome_source:
        Callable mapping an event ID to a measured post-merge outcome
        record (``{"outcome": ..., "merged": bool, ...}``). Injected so
        tests can replay recorded outcomes without network access.
    alpha:
        EMA smoothing factor used when reporting the expected update;
        the authoritative update happens inside the brain interface.
    allow_synthetic:
        Explicit offline-fixture simulation opt-in; never enable for production
        pattern stores. Synthetic learning is rejected by default, even when
        the caller supplied a measurement verifier.
    """

    def __init__(
        self,
        brain_interface: Any,
        outcome_source: Callable[[str], Optional[Mapping[str, Any]]],
        *,
        alpha: float = 0.3,
        evidence_store: Optional[EvidenceStore] = None,
        measurement_verifier: Optional[Callable[[Mapping[str, Any]], bool]] = None,
        allow_synthetic: bool = False,
    ) -> None:
        self.brain = brain_interface
        self.outcome_source = outcome_source
        self.alpha = alpha
        self.measurement_verifier = measurement_verifier
        if type(allow_synthetic) is not bool:
            raise EvidenceIntegrityError("allow_synthetic must be an explicit boolean")
        self.allow_synthetic = allow_synthetic
        store = evidence_store or getattr(outcome_source, "store", None)
        if store is None:
            root = getattr(brain_interface, "repo_root", None)
            if root is None:
                raise EvidenceIntegrityError("durable consumption store required")
            store = EvidenceStore(
                Path(root) / ".codex" / "improvement" / "outcome_consumption.jsonl",
                measurement_verifier=self.measurement_verifier,
                allow_synthetic=self.allow_synthetic,
            )
        self.evidence_store: EvidenceStore = store

    def process_outcome(
        self,
        *,
        event_id: str,
        pattern_id: str,
        patch_hash: str,
    ) -> Optional[ConfidenceUpdate]:
        """Update confidence from a verified outcome, or return None.

        Returns None (no update) when the outcome is missing, not merged,
        or not a measured terminal state — confidence must never move on
        unverified feedback.
        """

        record = self.outcome_source(event_id)
        if isinstance(record, Mapping) and type(record.get("synthetic", False)) is not bool:
            raise EvidenceIntegrityError("malformed synthetic marker")
        if (
            isinstance(record, Mapping)
            and record.get("synthetic") is True
            and not self.allow_synthetic
        ):
            raise EvidenceIntegrityError("synthetic learning requires explicit fixture-only opt-in")
        if record is None:
            return None
        with self._learning_guard():
            return self._process_outcome(
                event_id=event_id, pattern_id=pattern_id, patch_hash=patch_hash, record=record
            )

    @contextmanager
    def _learning_guard(self) -> Iterator[None]:
        """Serialize tracker writers only; other SDK writers must remain excluded."""
        path = getattr(self.brain, "pattern_store_path", None)
        if path is None:
            raise EvidenceIntegrityError("durable brain pattern store required")
        lock_path = Path(path).with_name(Path(path).name + ".outcome.lock")
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with open(lock_path, "a", encoding="utf-8") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def _process_outcome(
        self,
        *,
        event_id: str,
        pattern_id: str,
        patch_hash: str,
        record: Mapping[str, Any],
    ) -> Optional[ConfidenceUpdate]:
        if not isinstance(record, Mapping):
            raise EvidenceIntegrityError("malformed outcome record")
        if type(record.get("merged")) is not bool or record.get("outcome") not in (
            "pending",
            "success",
            "regression",
            "rollback",
        ):
            raise EvidenceIntegrityError("malformed outcome measurement")
        if not record.get("merged", False):
            logger.info("Event %s was not merged; skipping confidence update", event_id)
            return None

        outcome = str(record.get("outcome", "pending"))
        if outcome not in _MEASURED_OUTCOMES:
            logger.info("Outcome %r for event %s is not measured; skipping", outcome, event_id)
            return None
        for name, expected in (
            ("event_id", event_id),
            ("pattern_id", pattern_id),
            ("patch_hash", patch_hash),
        ):
            if not expected or record.get(name) != expected:
                raise EvidenceIntegrityError(f"outcome {name} mismatch")
        if not verified_measurement(
            record, self.measurement_verifier, allow_synthetic=self.allow_synthetic
        ):
            return None
        before = self._durable_pattern(pattern_id)
        pattern = self.brain.get_pattern(pattern_id)
        if pattern is None or before["success_rate"] != getattr(pattern, "success_rate", None):
            raise EvidenceIntegrityError("missing or stale brain pattern")
        cached = getattr(self.brain, "_patterns", None)
        if cached is not None:
            persisted = json.loads(Path(self.brain.pattern_store_path).read_text())["patterns"]
            if persisted != cached:
                raise EvidenceIntegrityError("stale brain snapshot; refresh before learning")
        store = self.evidence_store
        if not isinstance(self.outcome_source, _StoreOutcomeSource):
            store.record_outcome(
                event_id=event_id,
                pattern_id=pattern_id,
                patch_hash=patch_hash,
                merged=record["merged"],
                outcome=outcome,
                details=record.get("details"),
                observation_id=record.get("observation_id"),
                merged_sha=record.get("merged_sha"),
                provenance=record.get("provenance"),
                synthetic=record.get("synthetic", False),
            )
            persisted_record = store.observation_for(record)
            if persisted_record is None:
                raise EvidenceIntegrityError("outcome persistence failed")
            record = persisted_record
        if not store.claim_observation(record, measurement_verifier=self.measurement_verifier):
            return None

        previous_rate = self._current_rate(pattern_id)
        feedback = _OUTCOME_TO_FEEDBACK[outcome]
        applied = self.brain.submit_learning(
            pattern_id=pattern_id,
            outcome=feedback,
            context={"event_id": event_id, "patch_hash": patch_hash, "outcome": outcome},
            resolution_details=f"post-merge outcome={outcome} for event {event_id}",
        )
        if not applied:
            raise EvidenceIntegrityError("learning rejected; intent pending reconciliation")

        new_rate = self._current_rate(pattern_id)
        after = self._durable_pattern(pattern_id)
        if (
            after["success_rate"] != new_rate
            or after.get("times_applied") != before.get("times_applied", 0) + 1
        ):
            raise EvidenceIntegrityError("learning persistence unconfirmed; intent pending")
        with open(self.brain.pattern_store_path, "rb") as handle:
            os.fsync(handle.fileno())
        store.complete_observation(record, measurement_verifier=self.measurement_verifier)
        return ConfidenceUpdate(
            pattern_id=pattern_id,
            event_id=event_id,
            patch_hash=patch_hash,
            outcome=outcome,
            previous_rate=previous_rate,
            new_rate=new_rate,
            alpha=self.alpha,
            observation_key=store.observation_key(record),
            synthetic=record.get("synthetic", False),
        )

    def _durable_pattern(self, pattern_id: str) -> Mapping[str, Any]:
        try:
            data = json.loads(Path(self.brain.pattern_store_path).read_text(encoding="utf-8"))
            patterns = data["patterns"]
            if not isinstance(patterns, dict):
                raise ValueError("patterns must be an object")
            for pattern in patterns.values():
                if not isinstance(pattern, dict):
                    raise ValueError("pattern must be an object")
                if pattern.get("id") == pattern_id:
                    rate = pattern["success_rate"]
                    if type(rate) not in (int, float) or not 0 <= rate <= 1:
                        raise ValueError("invalid confidence")
                    return pattern
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise EvidenceIntegrityError("invalid durable brain pattern store") from exc
        raise EvidenceIntegrityError("pattern missing from durable store")

    def _current_rate(self, pattern_id: str) -> float:
        pattern = self.brain.get_pattern(pattern_id)
        if pattern is None:
            return 0.0
        return float(getattr(pattern, "success_rate", 0.0))
