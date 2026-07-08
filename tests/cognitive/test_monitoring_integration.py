"""Integration tests: Monitoring Sensor → Action Proposer → Self-Healing Validator pipeline.

Phase 7 — Cognitive Brain Testing & Validation
Tests the complete Cognitive Brain decision loop:
  1. MonitoringSensor senses system state
  2. ActionProposer proposes actions for detected failures
  3. ActionProposer executes (dry-run and live)
  4. SelfHealingValidator validates outcomes and adjusts confidence
  5. Confidence history feeds back into subsequent decisions
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module loading
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_sensor_mod = _load_module(
    _REPO_ROOT / "scripts" / "cognitive" / "sensors" / "monitoring_sensor.py",
    "monitoring_sensor",
)
_actions_mod = _load_module(
    _REPO_ROOT / "scripts" / "cognitive" / "actions" / "monitoring_actions.py",
    "monitoring_actions",
)
_shv_mod = _load_module(
    _REPO_ROOT / "scripts" / "cognitive" / "self_healing_validation.py",
    "self_healing_validation",
)

MonitoringSensor = _sensor_mod.MonitoringSensor
ActionProposer = _actions_mod.ActionProposer
SelfHealingValidator = _shv_mod.SelfHealingValidator

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def state_file(tmp_path: Path) -> Path:
    return tmp_path / "state.json"


@pytest.fixture()
def pipeline(tmp_path: Path):
    """Return (sensor, proposer, validator, state_file) wired to tmp_path."""
    sf = tmp_path / "state.json"
    return (
        MonitoringSensor(state_file=sf),
        ActionProposer(),
        SelfHealingValidator(history_file=tmp_path / "history.json"),
        sf,
    )


def _write_state(state_file: Path, workflows: dict) -> None:
    state_file.write_text(json.dumps({"workflows": workflows, "last_run": "2026-01-22T07:00:00Z"}))


# ---------------------------------------------------------------------------
# TestPipelineHealthySystem
# ---------------------------------------------------------------------------


class TestPipelineHealthySystem:
    def test_healthy_system_produces_no_failures(self, pipeline):
        sensor, proposer, validator, sf = pipeline
        _write_state(sf, {"wf_a": {"last_status": "success"}, "wf_b": {"last_status": "success"}})
        failures = sensor.get_active_failures()
        assert failures == [], "failures is not valid"

    def test_healthy_system_propose_returns_empty(self, pipeline):
        sensor, proposer, validator, sf = pipeline
        _write_state(sf, {"wf_a": {"last_status": "success"}})
        actions = proposer.propose_actions(sensor.get_active_failures())
        assert actions == [], "actions is not valid"

    def test_healthy_system_no_action_recommended(self, pipeline):
        sensor, proposer, validator, sf = pipeline
        _write_state(sf, {"wf_a": {"last_status": "success"}, "wf_b": {"last_status": "success"}})
        should_act, _, _ = sensor.should_propose_action()
        assert should_act is False, "should_act is not valid"


# ---------------------------------------------------------------------------
# TestPipelineCriticalFailure
# ---------------------------------------------------------------------------


class TestPipelineCriticalFailure:
    def test_critical_failure_detected_and_acted_on(self, pipeline):
        """Full path: severe failure → sensor detects → proposer generates rerun → dry-run."""
        sensor, proposer, validator, sf = pipeline
        _write_state(
            sf,
            {
                "wf_critical": {
                    "last_status": "failure",
                    "consecutive_failures": 8,
                    "failure_rate": 0.95,
                }
            },
        )
        failures = sensor.get_active_failures()
        assert len(failures) == 1, "Failures must not be empty"
        actions = proposer.propose_actions(failures)
        assert len(actions) == 1, "Actions must not be empty"
        assert actions[0]["action_type"] == "rerun_workflow", "Condition must be true"
        assert actions[0]["confidence"] >= proposer.confidence_threshold, "Value must be greater than zero"

    def test_dry_run_execution_returns_simulated(self, pipeline):
        # consecutive=8, failure_rate=0.9 → severity=0.84 ≥ 0.8 AND consecutive ≥ 3
        # → rerun_workflow, confidence=0.9 ≥ threshold → simulated
        sensor, proposer, validator, sf = pipeline
        _write_state(
            sf,
            {"wf_bad": {"last_status": "failure", "consecutive_failures": 8, "failure_rate": 0.9}},
        )
        actions = proposer.propose_actions(sensor.get_active_failures())
        results = [proposer.execute_action(a, dry_run=True) for a in actions]
        assert all(r["status"] == "simulated" for r in results), "Result must not be empty"

    def test_live_execution_returns_executed(self, pipeline):
        # consecutive=8, failure_rate=0.9 → severity=0.84 ≥ 0.8 AND consecutive ≥ 3
        # → rerun_workflow, confidence=0.9 ≥ threshold → executed
        sensor, proposer, validator, sf = pipeline
        _write_state(
            sf,
            {"wf_bad": {"last_status": "failure", "consecutive_failures": 8, "failure_rate": 0.9}},
        )
        actions = proposer.propose_actions(sensor.get_active_failures())
        results = [proposer.execute_action(a, dry_run=False) for a in actions]
        assert all(r["status"] == "executed" for r in results), "Result must not be empty"


# ---------------------------------------------------------------------------
# TestPipelineValidationFeedback
# ---------------------------------------------------------------------------


class TestPipelineValidationFeedback:
    def test_successful_action_validated_correctly(self, pipeline):
        sensor, proposer, validator, sf = pipeline
        _write_state(
            sf,
            {"wf_bad": {"last_status": "failure", "consecutive_failures": 5, "failure_rate": 0.8}},
        )
        actions = proposer.propose_actions(sensor.get_active_failures())
        validation = validator.validate_action_outcome(actions[0], {"status": "success"})
        assert validation["validation_status"] == "validated", "Condition must be true"
        assert validation["new_confidence"] > actions[0]["confidence"], "Value must be greater than zero"

    def test_failed_action_validated_with_lower_confidence(self, pipeline):
        sensor, proposer, validator, sf = pipeline
        _write_state(
            sf,
            {"wf_bad": {"last_status": "failure", "consecutive_failures": 5, "failure_rate": 0.8}},
        )
        actions = proposer.propose_actions(sensor.get_active_failures())
        validation = validator.validate_action_outcome(actions[0], {"status": "failure"})
        assert validation["validation_status"] == "failed", "Condition must be true"
        assert validation["new_confidence"] < actions[0]["confidence"], "Condition must be true"

    def test_confidence_improves_after_repeated_successes(self, pipeline):
        """Repeated successful cycles push stored confidence above initial proposer value."""
        sensor, proposer, validator, sf = pipeline
        _write_state(
            sf,
            {
                "wf_target": {
                    "last_status": "failure",
                    "consecutive_failures": 5,
                    "failure_rate": 0.8,
                }
            },
        )
        failures = sensor.get_active_failures()
        actions = proposer.propose_actions(failures)
        initial_confidence = actions[0]["confidence"]

        for _ in range(3):
            for action in actions:
                validator.validate_action_outcome(action, {"status": "success"})

        final_confidence = validator.get_confidence_for_action(
            actions[0]["action_type"], actions[0]["workflow"]
        )
        assert final_confidence >= initial_confidence, "final_confidence must be greater than zero"

    def test_confidence_decreases_after_repeated_failures(self, pipeline):
        sensor, proposer, validator, sf = pipeline
        _write_state(
            sf,
            {
                "wf_flaky": {
                    "last_status": "failure",
                    "consecutive_failures": 5,
                    "failure_rate": 0.8,
                }
            },
        )
        actions = proposer.propose_actions(sensor.get_active_failures())
        initial_confidence = actions[0]["confidence"]

        for _ in range(5):
            for action in actions:
                validator.validate_action_outcome(action, {"status": "failure"})

        final_confidence = validator.get_confidence_for_action(
            actions[0]["action_type"], actions[0]["workflow"]
        )
        assert final_confidence < initial_confidence, "final_confidence is not valid"


# ---------------------------------------------------------------------------
# TestPipelineExportIntegration
# ---------------------------------------------------------------------------


class TestPipelineExportIntegration:
    def test_export_feeds_actions(self, pipeline):
        """Export from sensor can drive action proposal directly."""
        sensor, proposer, validator, sf = pipeline
        _write_state(
            sf,
            {
                "wf_fail": {
                    "last_status": "failure",
                    "consecutive_failures": 4,
                    "failure_rate": 0.75,
                },
                "wf_ok": {"last_status": "success"},
            },
        )
        export = sensor.export_state_for_cognitive_brain()
        failures_from_export = export["active_failures"]
        actions = proposer.propose_actions(failures_from_export)
        assert len(actions) >= 1, "Actions must not be empty"
        assert all("action_type" in a for a in actions), "Condition must be true"

    def test_action_recommendation_in_export_consistent_with_get_failures(self, pipeline):
        """should_propose_action() result in export matches direct sensor call."""
        sensor, proposer, validator, sf = pipeline
        _write_state(
            sf,
            {"wf_a": {"last_status": "success"}, "wf_b": {"last_status": "success"}},
        )
        export = sensor.export_state_for_cognitive_brain()
        should_act_direct, _, _ = sensor.should_propose_action()
        should_act_export, _, _ = export["action_recommendation"]
        assert should_act_export == should_act_direct, "should_act_export is not valid"

    def test_full_loop_with_multiple_failures(self, pipeline):
        """Multiple high-severity failures → multiple rerun actions → all executed → all validated."""
        sensor, proposer, validator, sf = pipeline
        # Both workflows: severity ≥ 0.8 AND consecutive ≥ 3 → rerun_workflow, confidence=0.9
        _write_state(
            sf,
            {
                "wf_1": {"last_status": "failure", "consecutive_failures": 8, "failure_rate": 0.9},
                "wf_2": {"last_status": "failure", "consecutive_failures": 8, "failure_rate": 0.9},
            },
        )
        failures = sensor.get_active_failures()
        assert len(failures) == 2, "Failures must not be empty"
        actions = proposer.propose_actions(failures)
        assert len(actions) == 2, "Actions must not be empty"
        for action in actions:
            result = proposer.execute_action(action, dry_run=True)
            validation = validator.validate_action_outcome(action, {"status": "success"})
            assert result["status"] == "simulated", "Result must not be empty"
            assert validation["validation_status"] == "validated", "Condition must be true"

    def test_sensor_state_update_changes_pipeline_decisions(self, pipeline):
        """State change from healthy → failing should change action recommendations."""
        sensor, proposer, validator, sf = pipeline

        # Phase 1: healthy state
        _write_state(sf, {"wf_a": {"last_status": "success"}, "wf_b": {"last_status": "success"}})
        failures_before = sensor.get_active_failures()
        actions_before = proposer.propose_actions(failures_before)

        # Phase 2: introduce critical failure
        _write_state(
            sf,
            {
                "wf_a": {"last_status": "success"},
                "wf_b": {
                    "last_status": "failure",
                    "consecutive_failures": 5,
                    "failure_rate": 0.9,
                },
            },
        )
        failures_after = sensor.get_active_failures()
        actions_after = proposer.propose_actions(failures_after)

        assert len(actions_before) == 0, "Actions_before must not be empty"
        assert len(actions_after) > 0, "Actions_after must not be empty"
