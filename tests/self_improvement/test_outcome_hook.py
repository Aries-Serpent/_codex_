"""W3 acceptance: EvidenceStore-backed outcomes drive calibrated confidence.

The verified-outcome loop is closed when an outcome persisted via
``EvidenceStore.record_outcome`` is read back through the store's
``outcome_source`` adapter and only then updates pattern confidence.
"""

from __future__ import annotations

import json
from pathlib import Path

from aries_serpent_core.cognitive.brain_interface import AgentBrainInterface
from codex.cognitive_brain.evidence_store import EvidenceStore
from codex.cognitive_brain.outcome_tracking import OutcomeTracker, store_outcome_source

STORE = {
    "patterns": {
        "ci_timeout": {
            "id": "RP-019",
            "category": "ci_cd",
            "symptoms": ["ci job failure timeout"],
            "solutions": ["add timeout-minutes"],
            "success_rate": 0.9,
            "times_applied": 3,
        }
    }
}


def _brain(tmp_path: Path) -> AgentBrainInterface:
    store_dir = tmp_path / ".codex" / "cognitive_brain"
    store_dir.mkdir(parents=True, exist_ok=True)
    (store_dir / "pattern_learning_store.json").write_text(json.dumps(STORE))
    return AgentBrainInterface(agent_id="test-agent", repo_root=tmp_path, auto_register=False)


def _wired(tmp_path: Path) -> tuple[EvidenceStore, OutcomeTracker]:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    tracker = OutcomeTracker(_brain(tmp_path), outcome_source=store_outcome_source(store))
    return store, tracker


def test_persisted_success_outcome_updates_confidence(tmp_path: Path) -> None:
    store, tracker = _wired(tmp_path)
    store.record_outcome(
        event_id="e1", merged=True, outcome="success", pattern_id="RP-019", patch_hash="p"
    )
    update = tracker.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="p")
    assert update is not None
    assert update.new_rate > update.previous_rate


def test_persisted_regression_lowers_confidence(tmp_path: Path) -> None:
    store, tracker = _wired(tmp_path)
    store.record_outcome(
        event_id="e2", merged=True, outcome="regression", pattern_id="RP-019", patch_hash="p"
    )
    update = tracker.process_outcome(event_id="e2", pattern_id="RP-019", patch_hash="p")
    assert update is not None
    assert update.new_rate < update.previous_rate


def test_unmerged_persisted_outcome_does_not_update(tmp_path: Path) -> None:
    store, tracker = _wired(tmp_path)
    store.record_outcome(event_id="e3", merged=False, outcome="success", pattern_id="RP-019")
    assert tracker.process_outcome(event_id="e3", pattern_id="RP-019", patch_hash="p") is None


def test_pending_persisted_outcome_does_not_update(tmp_path: Path) -> None:
    store, tracker = _wired(tmp_path)
    store.record_outcome(event_id="e4", merged=True, outcome="pending", pattern_id="RP-019")
    assert tracker.process_outcome(event_id="e4", pattern_id="RP-019", patch_hash="p") is None


def test_unrecorded_event_does_not_update(tmp_path: Path) -> None:
    _, tracker = _wired(tmp_path)
    assert tracker.process_outcome(event_id="e5", pattern_id="RP-019", patch_hash="p") is None


def test_outcome_survives_store_restart(tmp_path: Path) -> None:
    path = tmp_path / "evidence.jsonl"
    EvidenceStore(path).record_outcome(
        event_id="e6", merged=True, outcome="success", pattern_id="RP-019", patch_hash="p"
    )
    recovered = EvidenceStore(path)
    tracker = OutcomeTracker(_brain(tmp_path), outcome_source=store_outcome_source(recovered))
    update = tracker.process_outcome(event_id="e6", pattern_id="RP-019", patch_hash="p")
    assert update is not None and update.outcome == "success"
