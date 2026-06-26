"""Unit tests for SelfHealingValidator (scripts/cognitive/self_healing_validation.py).

Phase 7 — Cognitive Brain Testing & Validation
Covers:
* validate_action_outcome(): success/failure confidence adjustment (+0.05/-0.1),
  confidence clamping [0.0, 1.0], required result fields, history persistence
* get_confidence_for_action(): default when no history, average of recent outcomes,
  last-10 window enforcement, workflow/action_type isolation
* _load_history() / _save_to_history(): persistence, 1000-entry cap
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Module loading
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SHV_PATH = _REPO_ROOT / "scripts" / "cognitive" / "self_healing_validation.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("self_healing_validation", _SHV_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_mod = _load_module()
SelfHealingValidator = _mod.SelfHealingValidator

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REQUIRED_RESULT_FIELDS = (
    "timestamp",
    "workflow",
    "action_type",
    "validation_status",
    "initial_confidence",
    "confidence_adjustment",
    "new_confidence",
    "success",
)


def _make_action(
    action_type: str = "rerun_workflow",
    workflow: str = "wf_test",
    confidence: float = 0.85,
) -> dict:
    return {"action_type": action_type, "workflow": workflow, "confidence": confidence}


def _make_outcome(success: bool = True) -> dict:
    return {"status": "success" if success else "failure"}


def _validator(tmp_path: Path) -> SelfHealingValidator:
    return SelfHealingValidator(history_file=tmp_path / "history.json")


# ---------------------------------------------------------------------------
# TestValidateActionOutcome
# ---------------------------------------------------------------------------


class TestValidateActionOutcome:
    def test_success_increases_confidence_by_005(self, tmp_path):
        v = _validator(tmp_path)
        result = v.validate_action_outcome(_make_action(confidence=0.85), _make_outcome(True))
        assert result["validation_status"] == "validated", "Result must not be empty"
        assert result["confidence_adjustment"] == 0.05, "Result must not be empty"
        assert abs(result["new_confidence"] - 0.90) < 1e-9, "Result must not be empty"
        assert result["success"] is True, "Result must not be empty"

    def test_failure_decreases_confidence_by_01(self, tmp_path):
        v = _validator(tmp_path)
        result = v.validate_action_outcome(_make_action(confidence=0.85), _make_outcome(False))
        assert result["validation_status"] == "failed", "Result must not be empty"
        assert result["confidence_adjustment"] == -0.1, "Result must not be empty"
        assert abs(result["new_confidence"] - 0.75) < 1e-9, "Result must not be empty"
        assert result["success"] is False, "Result must not be empty"

    def test_confidence_clamped_at_maximum_1(self, tmp_path):
        """confidence + 0.05 > 1.0 → clamped to 1.0."""
        v = _validator(tmp_path)
        result = v.validate_action_outcome(_make_action(confidence=0.99), _make_outcome(True))
        assert result["new_confidence"] <= 1.0, "Result must not be empty"
        assert result["new_confidence"] == 1.0, "Result must not be empty"

    def test_confidence_clamped_at_minimum_0(self, tmp_path):
        """confidence - 0.1 < 0.0 → clamped to 0.0."""
        v = _validator(tmp_path)
        result = v.validate_action_outcome(_make_action(confidence=0.05), _make_outcome(False))
        assert result["new_confidence"] >= 0.0, "Value must be greater than zero"
        assert result["new_confidence"] == 0.0, "Result must not be empty"

    def test_confidence_at_exactly_1_stays_clamped_on_success(self, tmp_path):
        v = _validator(tmp_path)
        result = v.validate_action_outcome(_make_action(confidence=1.0), _make_outcome(True))
        assert result["new_confidence"] == 1.0, "Result must not be empty"

    def test_confidence_at_exactly_0_stays_clamped_on_failure(self, tmp_path):
        v = _validator(tmp_path)
        result = v.validate_action_outcome(_make_action(confidence=0.0), _make_outcome(False))
        assert result["new_confidence"] == 0.0, "Result must not be empty"

    def test_result_contains_all_required_fields(self, tmp_path):
        v = _validator(tmp_path)
        result = v.validate_action_outcome(_make_action(), _make_outcome())
        for field in _REQUIRED_RESULT_FIELDS:
            assert field in result, f"Missing field: {field}"

    def test_result_preserves_workflow_and_action_type(self, tmp_path):
        v = _validator(tmp_path)
        result = v.validate_action_outcome(
            _make_action(action_type="analyze_logs", workflow="my_wf"), _make_outcome()
        )
        assert result["workflow"] == "my_wf", "Result must not be empty"
        assert result["action_type"] == "analyze_logs", "Result must not be empty"

    def test_result_saved_to_history_file(self, tmp_path):
        history_file = tmp_path / "history.json"
        v = SelfHealingValidator(history_file=history_file)
        v.validate_action_outcome(_make_action(), _make_outcome())
        saved = json.loads(history_file.read_text())
        assert len(saved) == 1, "Saved must not be empty"
        assert "timestamp" in saved[0], "Condition must be true"

    def test_multiple_outcomes_accumulated_in_history(self, tmp_path):
        v = _validator(tmp_path)
        for i in range(5):
            v.validate_action_outcome(_make_action(), _make_outcome(i % 2 == 0))
        history = v._load_history()
        assert len(history) == 5, "History must not be empty"

    def test_timestamp_is_iso_format(self, tmp_path):
        v = _validator(tmp_path)
        result = v.validate_action_outcome(_make_action(), _make_outcome())
        assert "T" in result["timestamp"], "Result must not be empty"

    def test_initial_confidence_recorded_correctly(self, tmp_path):
        v = _validator(tmp_path)
        result = v.validate_action_outcome(_make_action(confidence=0.72), _make_outcome())
        assert result["initial_confidence"] == 0.72, "Result must not be empty"


# ---------------------------------------------------------------------------
# TestGetConfidenceForAction
# ---------------------------------------------------------------------------


class TestGetConfidenceForAction:
    def test_default_07_when_no_history(self, tmp_path):
        v = _validator(tmp_path)
        assert v.get_confidence_for_action("rerun_workflow", "wf_test") == 0.7

    def test_single_success_returns_adjusted_confidence(self, tmp_path):
        v = _validator(tmp_path)
        v.validate_action_outcome(_make_action(confidence=0.80), _make_outcome(True))
        # new_confidence = 0.80 + 0.05 = 0.85
        conf = v.get_confidence_for_action("rerun_workflow", "wf_test")
        assert abs(conf - 0.85) < 1e-9, "Condition must be true"

    def test_average_of_multiple_successes(self, tmp_path):
        """3 actions all starting at 0.80 → each produces new_confidence=0.85 → avg=0.85."""
        v = _validator(tmp_path)
        for _ in range(3):
            v.validate_action_outcome(_make_action(confidence=0.80), _make_outcome(True))
        conf = v.get_confidence_for_action("rerun_workflow", "wf_test")
        assert abs(conf - 0.85) < 1e-9, "Condition must be true"

    def test_last_10_window_ignores_older_entries(self, tmp_path):
        """16 entries: first 15 failures then 1 success → last-10 avg computed correctly."""
        v = _validator(tmp_path)
        for _ in range(15):
            # failure: new_confidence = 0.9 - 0.1 = 0.8
            v.validate_action_outcome(_make_action(confidence=0.9), _make_outcome(False))
        # success: new_confidence = 0.9 + 0.05 = 0.95
        v.validate_action_outcome(_make_action(confidence=0.9), _make_outcome(True))
        # last 10: indices 6-14 (9 failures → 0.8) + index 15 (1 success → 0.95)
        # avg = (9*0.8 + 0.95) / 10 = 8.15/10 = 0.815
        conf = v.get_confidence_for_action("rerun_workflow", "wf_test")
        assert abs(conf - 0.815) < 1e-6, "Condition must be true"

    def test_different_workflow_not_mixed(self, tmp_path):
        """History for wf_b should not affect confidence for wf_a."""
        v = _validator(tmp_path)
        for _ in range(5):
            v.validate_action_outcome(
                _make_action(workflow="wf_b", confidence=0.5), _make_outcome(True)
            )
        conf = v.get_confidence_for_action("rerun_workflow", "wf_a")
        assert conf == 0.7, "conf is not valid"

    def test_different_action_type_not_mixed(self, tmp_path):
        """History for analyze_logs should not affect confidence for rerun_workflow."""
        v = _validator(tmp_path)
        for _ in range(5):
            v.validate_action_outcome(
                _make_action(action_type="analyze_logs", confidence=0.5), _make_outcome(True)
            )
        conf = v.get_confidence_for_action("rerun_workflow", "wf_test")
        assert conf == 0.7, "conf is not valid"

    def test_confidence_reflects_mixed_success_failure(self, tmp_path):
        """5 successes then 5 failures → last-10 contains all; average expected."""
        v = _validator(tmp_path)
        for _ in range(5):
            # success: 0.8 + 0.05 = 0.85
            v.validate_action_outcome(_make_action(confidence=0.8), _make_outcome(True))
        for _ in range(5):
            # failure: 0.8 - 0.1 = 0.7
            v.validate_action_outcome(_make_action(confidence=0.8), _make_outcome(False))
        conf = v.get_confidence_for_action("rerun_workflow", "wf_test")
        # avg = (5*0.85 + 5*0.70) / 10 = (4.25 + 3.50) / 10 = 0.775
        assert abs(conf - 0.775) < 1e-6, "Condition must be true"


# ---------------------------------------------------------------------------
# TestHistoryPersistence
# ---------------------------------------------------------------------------


class TestHistoryPersistence:
    def test_history_persists_across_instances(self, tmp_path):
        history_file = tmp_path / "history.json"
        v1 = SelfHealingValidator(history_file=history_file)
        v1.validate_action_outcome(_make_action(), _make_outcome(True))
        v2 = SelfHealingValidator(history_file=history_file)
        history = v2._load_history()
        assert len(history) == 1, "History must not be empty"

    def test_empty_history_file_returns_empty_list(self, tmp_path):
        history_file = tmp_path / "history.json"
        history_file.write_text("[]")
        v = SelfHealingValidator(history_file=history_file)
        assert v._load_history() == [], "Condition must be true"

    def test_missing_history_file_returns_empty_list(self, tmp_path):
        v = SelfHealingValidator(history_file=tmp_path / "no_history.json")
        assert v._load_history() == [], "Condition must be true"

    def test_history_capped_at_1000_entries(self, tmp_path):
        """After 1001 saves, history file should have at most 1000 entries."""
        history_file = tmp_path / "history.json"
        # Pre-seed 1001 entries directly
        entries = [
            {
                "action_type": "rerun_workflow",
                "workflow": "wf_t",
                "success": True,
                "new_confidence": 0.8,
                "timestamp": "2026-01-22T00:00:00Z",
                "validation_status": "validated",
                "initial_confidence": 0.75,
                "confidence_adjustment": 0.05,
            }
            for _ in range(1001)
        ]
        history_file.write_text(json.dumps(entries))
        v = SelfHealingValidator(history_file=history_file)
        # Trigger one more save — should truncate to 1000
        v.validate_action_outcome(_make_action(), _make_outcome())
        saved = json.loads(history_file.read_text())
        assert len(saved) <= 1000, "Saved must not be empty"

    def test_parent_dirs_created_automatically(self, tmp_path):
        """SelfHealingValidator creates parent dir of history_file if missing."""
        history_file = tmp_path / "deep" / "nested" / "history.json"
        v = SelfHealingValidator(history_file=history_file)
        # Should not raise; parent dir should exist
        assert v.history_file.parent.exists(), "Condition must be true"

    def test_load_history_resilient_to_corrupt_file(self, tmp_path):
        """Corrupt JSON in history file → returns [] gracefully."""
        history_file = tmp_path / "history.json"
        history_file.write_text("NOT VALID JSON {{{")
        v = SelfHealingValidator(history_file=history_file)
        assert v._load_history() == [], "Condition must be true"
