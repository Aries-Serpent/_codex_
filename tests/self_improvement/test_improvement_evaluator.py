"""W4 acceptance: evaluator renders complete/partial/unverified from the trail."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from codex.cognitive_brain.evidence_store import EvidenceStore
from codex.cognitive_brain.improvement_evaluator import (
    COMPLETE,
    PARTIAL,
    UNVERIFIED,
    evaluate_event,
    evaluate_store,
)

_EVENT = {
    "event_id": "e1",
    "repo": "o/r",
    "sha": "a" * 40,
    "schema_version": "1.0.0",
    "signal": {
        "source": "pda_failure_log",
        "kind": "ci_job_failure",
        "measured_at": "2026-10-21T00:00:00Z",
        "availability": "measured",
    },
    "pattern": {"pattern_id": "RP-019", "pattern_version": "3", "success_rate": 0.9},
    "proposal": {
        "patch_hash": "b" * 64,
        "files": ["src/x.py"],
        "diff_lines": 5,
        "required_gates": ["compile", "tests"],
    },
}


def _full_store(tmp_path: Path) -> EvidenceStore:
    store = EvidenceStore(tmp_path / "evidence.jsonl", allow_synthetic=True)
    store.record_event(_EVENT)
    store.record(
        "execution",
        "e1",
        {
            "status": "verified",
            "patch_hash": "b" * 64,
            "base_sha": "a" * 40,
            "attempt_id": "fixture-attempt",
            "candidate_tree_hash": "f" * 40,
            "authority": {"authorized": True, "reasons": [], "idempotency_key": "e1"},
            "required_gates": ["compile", "tests"],
            "baseline_gate_logs": [
                {
                    "name": name,
                    "returncode": 1 if name == "tests" else 0,
                    "status": "failed" if name == "tests" else "passed",
                    "command": ["python", "-m", "compileall" if name == "compile" else "pytest"],
                    "output_hash": "e" * 64,
                }
                for name in ("tests",)
            ],
            "gate_logs": [
                {
                    "name": name,
                    "returncode": 0,
                    "status": "passed",
                    "command": ["python", "-m", "compileall" if name == "compile" else "pytest"],
                    "output_hash": "d" * 64,
                }
                for name in ("compile", "tests")
            ],
        },
    )
    store.record(
        "pr",
        "e1",
        {
            "merge_state": "merged",
            "pr_number": 7,
            "patch_hash": "b" * 64,
            "merged_sha": "c" * 40,
            "attempt_id": "fixture-attempt",
            "base_sha": "a" * 40,
            "merged_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    store.record_outcome(
        event_id="e1",
        merged=True,
        outcome="success",
        pattern_id="RP-019",
        patch_hash="b" * 64,
        synthetic=True,
        merged_sha="c" * 40,
        observation_id="fixture-observation",
        details={"attempt_id": "fixture-attempt", "base_sha": "a" * 40},
        provenance={
            "source": "synthetic-fixture",
            "measured_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    outcome = store.outcome_for("e1")
    assert outcome is not None
    assert store.claim_observation(outcome)
    store.complete_observation(outcome)
    store.record(
        "confidence",
        "e1",
        {
            "pattern_id": "RP-019",
            "new_rate": 0.93,
            "patch_hash": "b" * 64,
            "merged_sha": "c" * 40,
            "attempt_id": "fixture-attempt",
            "base_sha": "a" * 40,
            "outcome": "success",
            "observation_key": store.observation_key(outcome),
        },
    )
    return store


def test_complete_chain_returns_complete(tmp_path: Path) -> None:
    report = evaluate_event(_full_store(tmp_path), "e1", allow_synthetic=True)
    assert report.verdict == COMPLETE
    assert report.missing == ()
    assert all(report.links.values())
    assert report.proof_scope == "synthetic"


def test_missing_link_returns_partial(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    store.record_event(_EVENT)
    store.record(
        "execution", "e1", {"status": "verified", "gate_logs": [{"name": "t", "returncode": 0}]}
    )
    report = evaluate_event(store, "e1")
    assert report.verdict == PARTIAL
    assert "pr" in report.missing and "confidence_update" in report.missing


def test_unknown_event_is_unverified(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    assert evaluate_event(store, "nope").verdict == UNVERIFIED


def test_unmeasured_signal_breaks_chain(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    bad = dict(_EVENT)
    bad["signal"] = {**_EVENT["signal"], "availability": "unavailable"}
    store.record_event(bad)
    report = evaluate_event(store, "e1")
    assert report.verdict == PARTIAL
    assert "signal" in report.missing


def test_evaluate_store_covers_all_events(tmp_path: Path) -> None:
    store = _full_store(tmp_path)
    store.record_event({**_EVENT, "event_id": "e2"})
    reports = {r.event_id: r.verdict for r in evaluate_store(store, allow_synthetic=True)}
    assert reports == {"e1": COMPLETE, "e2": PARTIAL}
