"""W4 acceptance: evaluator renders complete/partial/unverified from the trail."""

from __future__ import annotations

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
    "sha": "abc",
    "schema_version": "1.0.0",
    "signal": {"source": "pda_failure_log", "kind": "ci_job_failure",
               "measured_at": "2026-10-21T00:00:00Z", "availability": "measured"},
    "pattern": {"pattern_id": "RP-019", "pattern_version": "3", "success_rate": 0.9},
    "proposal": {"patch_hash": "p", "files": ["src/x.py"], "diff_lines": 5},
}


def _full_store(tmp_path: Path) -> EvidenceStore:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    store.record_event(_EVENT)
    store.record("execution", "e1", {"status": "verified",
                                     "gate_logs": [{"name": "tests", "returncode": 0}]})
    store.record("pr", "e1", {"merge_state": "merged", "pr_number": 7})
    store.record_outcome(event_id="e1", merged=True, outcome="success",
                         pattern_id="RP-019", patch_hash="p")
    store.record("confidence", "e1", {"pattern_id": "RP-019", "new_rate": 0.93})
    return store


def test_complete_chain_returns_complete(tmp_path: Path) -> None:
    report = evaluate_event(_full_store(tmp_path), "e1")
    assert report.verdict == COMPLETE
    assert report.missing == ()
    assert all(report.links.values())


def test_missing_link_returns_partial(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    store.record_event(_EVENT)
    store.record("execution", "e1", {"status": "verified",
                                     "gate_logs": [{"name": "t", "returncode": 0}]})
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
    reports = {r.event_id: r.verdict for r in evaluate_store(store)}
    assert reports == {"e1": COMPLETE, "e2": PARTIAL}
