"""Stage 5 acceptance: durable evidence store, idempotency, circuit breakers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from codex.cognitive_brain.evidence_store import EvidenceStore


def _event(event_id: str) -> dict:
    return {"event_id": event_id, "repo": "o/r", "sha": "abc", "schema_version": "1.0.0"}


def test_events_are_idempotent(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    assert store.record_event(_event("e1")) is True
    assert store.record_event(_event("e1")) is False
    assert store.seen("e1")


def test_outcome_round_trip_and_audit(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    store.record_event(_event("e1"))
    store.record_outcome(
        event_id="e1", merged=True, outcome="success", pattern_id="RP-019", patch_hash="p"
    )
    assert store.outcome_for("e1")["outcome"] == "success"
    trail = store.audit_trail("e1")
    assert {r["kind"] for r in trail} == {"event", "outcome"}


def test_restart_recovers_evidence_and_idempotency(tmp_path: Path) -> None:
    path = tmp_path / "evidence.jsonl"
    EvidenceStore(path).record_event(_event("e1"))
    recovered = EvidenceStore(path)
    assert recovered.seen("e1")
    assert recovered.record_event(_event("e1")) is False


def test_repeated_failures_trip_circuit_breaker(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    for i in range(3):
        store.record_outcome(
            event_id=f"e{i}", merged=True, outcome="rollback", pattern_id="RP-019"
        )
    assert not store.pattern_enabled("RP-019")
    assert "consecutive" in store.disable_reason("RP-019")
    # Audit history retained despite disabling.
    assert len(store.audit_trail()) == 3


def test_success_resets_failure_streak(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    for outcome in ("rollback", "success", "rollback"):
        store.record_outcome(
            event_id=f"e-{outcome}", merged=True, outcome=outcome, pattern_id="RP-1"
        )
    assert store.pattern_enabled("RP-1")


def test_stale_pattern_is_disabled(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    stale = (datetime.now(timezone.utc) - timedelta(days=120)).isoformat()
    assert not store.pattern_enabled("RP-OLD", last_used_iso=stale)
    assert "stale" in store.disable_reason("RP-OLD")


def test_backup_and_restore(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    store.record_event(_event("e1"))
    backup = store.backup(tmp_path / "backup" / "evidence.jsonl")
    restored = EvidenceStore(backup)
    assert restored.seen("e1")
