"""Stage 4 acceptance: verified outcomes drive calibrated confidence updates."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from aries_serpent_core.cognitive.brain_interface import AgentBrainInterface
from codex.cognitive_brain.outcome_tracking import OutcomeTracker

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


def _tracker(tmp_path: Path, outcomes: dict) -> OutcomeTracker:
    outcomes = {
        event_id: {
            **record,
            "event_id": event_id,
            "pattern_id": "RP-019",
            "patch_hash": "p",
            "synthetic": True,
        }
        for event_id, record in outcomes.items()
    }
    return OutcomeTracker(_brain(tmp_path), outcome_source=outcomes.get, allow_synthetic=True)


def test_outcome_helpers_without_posix_dependencies(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import sys
sys.modules["fcntl"] = None
from codex.cognitive_brain.outcome_tracking import (
    OutcomeTracker, store_outcome_source, verified_measurement,
)
assert not verified_measurement({"merged": False})
assert "codex.cognitive_brain.evidence_store" not in sys.modules
class Store:
    def outcome_for(self, event_id):
        return {"event_id": event_id}
assert store_outcome_source(Store())("fixture") == {"event_id": "fixture"}
try:
    OutcomeTracker(None, lambda _: None)
except RuntimeError as exc:
    assert str(exc) == "Outcome learning requires POSIX fcntl locking"
else:
    raise AssertionError("POSIX-only learning must fail explicitly")
""",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_successful_merged_outcome_updates_confidence(tmp_path: Path) -> None:
    tracker = _tracker(tmp_path, {"e1": {"merged": True, "outcome": "success"}})
    update = tracker.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="p")
    assert update is not None
    assert update.previous_rate == 0.9
    assert update.new_rate > update.previous_rate  # success nudges EMA up


def test_regression_outcome_lowers_confidence(tmp_path: Path) -> None:
    tracker = _tracker(tmp_path, {"e2": {"merged": True, "outcome": "regression"}})
    update = tracker.process_outcome(event_id="e2", pattern_id="RP-019", patch_hash="p")
    assert update is not None
    assert update.new_rate < update.previous_rate


def test_unmerged_pr_never_updates_confidence(tmp_path: Path) -> None:
    tracker = _tracker(tmp_path, {"e3": {"merged": False, "outcome": "success"}})
    assert tracker.process_outcome(event_id="e3", pattern_id="RP-019", patch_hash="p") is None


def test_pending_outcome_never_updates_confidence(tmp_path: Path) -> None:
    tracker = _tracker(tmp_path, {"e4": {"merged": True, "outcome": "pending"}})
    assert tracker.process_outcome(event_id="e4", pattern_id="RP-019", patch_hash="p") is None


def test_missing_outcome_never_updates_confidence(tmp_path: Path) -> None:
    tracker = _tracker(tmp_path, {})
    assert tracker.process_outcome(event_id="e5", pattern_id="RP-019", patch_hash="p") is None
