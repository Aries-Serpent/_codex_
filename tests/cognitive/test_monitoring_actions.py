"""Unit tests for ActionProposer (scripts/cognitive/actions/monitoring_actions.py).

Phase 7 — Cognitive Brain Testing & Validation
Covers:
* ActionProposer.propose_actions(): severity/consecutive thresholds, action types, confidence
* ActionProposer.execute_action(): confidence threshold gate, dry-run mode, approval gate,
  live execution paths (rerun_workflow, analyze_logs, generic), error resilience
* confidence_threshold default value
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

# ---------------------------------------------------------------------------
# Module loading
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]
_ACTIONS_PATH = _REPO_ROOT / "scripts" / "cognitive" / "actions" / "monitoring_actions.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("monitoring_actions", _ACTIONS_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_mod = _load_module()
ActionProposer = _mod.ActionProposer

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_failure(
    workflow: str = "wf_test",
    severity: float = 0.9,
    consecutive: int = 5,
    failure_rate: float = 0.8,
) -> dict:
    return {
        "workflow": workflow,
        "severity": severity,
        "consecutive_failures": consecutive,
        "failure_rate": failure_rate,
    }


def _make_action(
    action_type: str = "rerun_workflow",
    workflow: str = "wf_test",
    confidence: float = 0.9,
    requires_approval: bool = False,
) -> dict:
    return {
        "action_type": action_type,
        "workflow": workflow,
        "confidence": confidence,
        "requires_approval": requires_approval,
    }


# ---------------------------------------------------------------------------
# TestActionProposerInit
# ---------------------------------------------------------------------------


class TestActionProposerInit:
    def test_default_confidence_threshold(self):
        proposer = ActionProposer()
        assert proposer.confidence_threshold == 0.8, "confidence_threshold is not valid"

    def test_instantiation_no_args(self):
        proposer = ActionProposer()
        assert proposer is not None, "proposer must be initialized"


# ---------------------------------------------------------------------------
# TestProposeActions
# ---------------------------------------------------------------------------


class TestProposeActions:
    def test_empty_failures_returns_empty(self):
        assert ActionProposer().propose_actions([]) == [], "Condition must be true"

    def test_high_severity_produces_rerun(self):
        """severity ≥ 0.8 AND consecutive ≥ 3 → rerun_workflow, confidence=0.9, risk=low."""
        proposer = ActionProposer()
        actions = proposer.propose_actions([_make_failure(severity=0.9, consecutive=5)])
        assert len(actions) == 1, "Actions must not be empty"
        a = actions[0]
        assert a["action_type"] == "rerun_workflow", "Condition must be true"
        assert a["confidence"] == 0.9, "Condition must be true"
        assert a["risk"] == "low", "Condition must be true"
        assert a["requires_approval"] is False, "Condition must be true"

    def test_medium_severity_produces_analyze_logs(self):
        """0.5 ≤ severity < 0.8 AND consecutive ≥ 2 → analyze_logs, confidence=0.75."""
        proposer = ActionProposer()
        actions = proposer.propose_actions([_make_failure(severity=0.6, consecutive=3)])
        assert len(actions) == 1, "Actions must not be empty"
        a = actions[0]
        assert a["action_type"] == "analyze_logs", "Condition must be true"
        assert a["confidence"] == 0.75, "Condition must be true"

    def test_low_severity_produces_monitor(self):
        """Below medium threshold → monitor, confidence=0.6, risk=none."""
        proposer = ActionProposer()
        actions = proposer.propose_actions([_make_failure(severity=0.3, consecutive=1)])
        assert len(actions) == 1, "Actions must not be empty"
        a = actions[0]
        assert a["action_type"] == "monitor", "Condition must be true"
        assert a["confidence"] == 0.6, "Condition must be true"
        assert a["risk"] == "none", "Condition must be true"

    def test_boundary_high_severity_exactly_08_and_3_consecutive(self):
        """Boundary: severity=0.8 AND consecutive=3 → rerun_workflow (meets threshold exactly)."""
        proposer = ActionProposer()
        actions = proposer.propose_actions([_make_failure(severity=0.8, consecutive=3)])
        assert actions[0]["action_type"] == "rerun_workflow", "Condition must be true"

    def test_boundary_high_severity_08_only_2_consecutive_falls_to_medium(self):
        """severity=0.8 but only 2 consecutive → does NOT trigger rerun; drops to medium or monitor."""
        proposer = ActionProposer()
        actions = proposer.propose_actions([_make_failure(severity=0.8, consecutive=2)])
        # consecutive < 3, so high-severity branch skipped → medium or monitor
        assert actions[0]["action_type"] in ("analyze_logs", "monitor")

    def test_boundary_medium_severity_exactly_05(self):
        """severity=0.5 AND consecutive ≥ 2 → analyze_logs."""
        proposer = ActionProposer()
        actions = proposer.propose_actions([_make_failure(severity=0.5, consecutive=2)])
        assert actions[0]["action_type"] == "analyze_logs", "Condition must be true"

    def test_multiple_failures_produce_one_action_each(self):
        proposer = ActionProposer()
        failures = [
            _make_failure("wf_a", severity=0.9, consecutive=5),
            _make_failure("wf_b", severity=0.6, consecutive=3),
            _make_failure("wf_c", severity=0.2, consecutive=1),
        ]
        actions = proposer.propose_actions(failures)
        assert len(actions) == 3, "Actions must not be empty"

    def test_workflow_name_preserved(self):
        proposer = ActionProposer()
        actions = proposer.propose_actions([_make_failure(workflow="my_pipeline")])
        assert actions[0]["workflow"] == "my_pipeline", "Condition must be true"

    def test_action_contains_reason(self):
        proposer = ActionProposer()
        actions = proposer.propose_actions([_make_failure()])
        assert "reason" in actions[0], "Condition must be true"
        assert isinstance(actions[0]["reason"], str)

    def test_action_contains_requires_approval(self):
        proposer = ActionProposer()
        actions = proposer.propose_actions([_make_failure()])
        assert "requires_approval" in actions[0], "Condition must be true"


# ---------------------------------------------------------------------------
# TestExecuteAction
# ---------------------------------------------------------------------------


class TestExecuteAction:
    def test_below_threshold_is_skipped(self):
        """confidence < 0.8 → status=skipped, reason mentions confidence value."""
        proposer = ActionProposer()
        result = proposer.execute_action(_make_action(confidence=0.5), dry_run=False)
        assert result["status"] == "skipped", "Result must not be empty"
        assert "0.5" in result["reason"], "Result must not be empty"

    def test_confidence_exactly_at_threshold_is_not_skipped(self):
        """confidence == 0.8 (not strictly below threshold) → should execute in dry_run."""
        proposer = ActionProposer()
        result = proposer.execute_action(_make_action(confidence=0.8), dry_run=True)
        assert result["status"] == "simulated", "Result must not be empty"

    def test_requires_approval_live_returns_pending(self):
        """requires_approval=True AND dry_run=False → status=pending_approval."""
        proposer = ActionProposer()
        result = proposer.execute_action(
            _make_action(confidence=0.9, requires_approval=True), dry_run=False
        )
        assert result["status"] == "pending_approval", "Result must not be empty"

    def test_requires_approval_dry_run_still_simulates(self):
        """requires_approval=True BUT dry_run=True → dry_run check occurs first → simulated."""
        proposer = ActionProposer()
        result = proposer.execute_action(
            _make_action(confidence=0.9, requires_approval=True), dry_run=True
        )
        assert result["status"] == "simulated", "Result must not be empty"

    def test_dry_run_true_returns_simulated(self):
        proposer = ActionProposer()
        result = proposer.execute_action(_make_action(confidence=0.9), dry_run=True)
        assert result["status"] == "simulated", "Result must not be empty"
        assert result["action_type"] == "rerun_workflow", "Result must not be empty"
        assert result["workflow"] == "wf_test", "Result must not be empty"
        assert "Would execute" in result["message"], "Result must not be empty"

    def test_dry_run_default_is_true(self):
        """execute_action() with no dry_run arg → defaults to dry_run=True → simulated."""
        proposer = ActionProposer()
        result = proposer.execute_action(_make_action(confidence=0.9))
        assert result["status"] == "simulated", "Result must not be empty"

    def test_live_rerun_workflow_executed(self):
        proposer = ActionProposer()
        result = proposer.execute_action(
            _make_action(action_type="rerun_workflow", confidence=0.9), dry_run=False
        )
        assert result["status"] == "executed", "Result must not be empty"
        assert result["action_type"] == "rerun_workflow", "Result must not be empty"

    def test_live_analyze_logs_executed(self):
        proposer = ActionProposer()
        result = proposer.execute_action(
            _make_action(action_type="analyze_logs", confidence=0.9), dry_run=False
        )
        assert result["status"] == "executed", "Result must not be empty"
        assert result["action_type"] == "analyze_logs", "Result must not be empty"

    def test_live_generic_action_executed(self):
        """Unknown action_type still returns executed (fallback path)."""
        proposer = ActionProposer()
        result = proposer.execute_action(
            _make_action(action_type="monitor", confidence=0.9), dry_run=False
        )
        assert result["status"] == "executed", "Result must not be empty"

    def test_simulated_result_contains_workflow(self):
        proposer = ActionProposer()
        result = proposer.execute_action(_make_action(workflow="pipeline_x", confidence=0.9))
        assert result["workflow"] == "pipeline_x", "Result must not be empty"

    def test_confidence_just_below_threshold(self):
        """confidence=0.799 < 0.8 → skipped."""
        proposer = ActionProposer()
        result = proposer.execute_action(_make_action(confidence=0.799), dry_run=False)
        assert result["status"] == "skipped", "Result must not be empty"

    def test_confidence_just_above_threshold(self):
        """confidence=0.801 > 0.8 → not skipped."""
        proposer = ActionProposer()
        result = proposer.execute_action(_make_action(confidence=0.801), dry_run=True)
        assert result["status"] == "simulated", "Result must not be empty"
