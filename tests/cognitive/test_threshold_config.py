"""Phase 8a tests for configurable monitoring thresholds."""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ACTIONS_PATH = _REPO_ROOT / "scripts" / "cognitive" / "actions" / "monitoring_actions.py"
_SENSOR_PATH = _REPO_ROOT / "scripts" / "cognitive" / "sensors" / "monitoring_sensor.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_actions_mod = _load(_ACTIONS_PATH, "monitoring_actions_threshold")
_sensor_mod = _load(_SENSOR_PATH, "monitoring_sensor_threshold")
ActionProposer = _actions_mod.ActionProposer
MonitoringSensor = _sensor_mod.MonitoringSensor


def _write_config(path: Path, body: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)


def _state_path(tmp_path: Path, workflows: dict[str, dict]) -> Path:
    p = tmp_path / "monitor_state.json"
    p.write_text(json.dumps({"workflows": workflows, "last_run": "2026-05-14T00:00:00Z"}))
    return p


class TestActionThresholdConfig:
    def test_defaults_used_when_config_missing(self, tmp_path):
        proposer = ActionProposer(config_file=tmp_path / "missing.yaml")
        assert proposer.confidence_threshold == 0.8, "confidence_threshold is not valid"
        actions = proposer.propose_actions(
            [{"workflow": "wf", "severity": 0.8, "consecutive_failures": 3}]
        )
        assert actions[0]["action_type"] == "rerun_workflow", "Condition must be true"

    def test_global_thresholds_loaded_from_yaml(self, tmp_path):
        cfg = tmp_path / "monitoring.yaml"
        _write_config(
            cfg,
            """
cognitive_brain:
  thresholds:
    severity_threshold: 0.7
    consecutive_threshold: 4
    confidence_threshold: 0.9
    per_workflow_overrides: {}
""".strip(),
        )
        proposer = ActionProposer(config_file=cfg)
        actions = proposer.propose_actions(
            [{"workflow": "wf", "severity": 0.75, "consecutive_failures": 4}]
        )
        assert actions[0]["action_type"] == "rerun_workflow", "Condition must be true"
        skipped = proposer.execute_action(
            {
                "action_type": "rerun_workflow",
                "workflow": "wf",
                "confidence": 0.85,
                "requires_approval": False,
            },
            dry_run=False,
        )
        assert skipped["status"] == "skipped", "Condition must be true"

    def test_per_workflow_override_applied(self, tmp_path):
        cfg = tmp_path / "monitoring.yaml"
        _write_config(
            cfg,
            """
cognitive_brain:
  thresholds:
    severity_threshold: 0.8
    consecutive_threshold: 3
    confidence_threshold: 0.8
    per_workflow_overrides:
      wf_strict:
        confidence_threshold: 0.95
""".strip(),
        )
        proposer = ActionProposer(config_file=cfg)
        strict_result = proposer.execute_action(
            {"action_type": "monitor", "workflow": "wf_strict", "confidence": 0.9},
            dry_run=False,
        )
        default_result = proposer.execute_action(
            {"action_type": "monitor", "workflow": "wf_default", "confidence": 0.9},
            dry_run=False,
        )
        assert strict_result["status"] == "skipped", "Result must not be empty"
        assert default_result["status"] == "executed", "Result must not be empty"

    def test_hot_reload_without_restart(self, tmp_path):
        cfg = tmp_path / "monitoring.yaml"
        _write_config(
            cfg,
            """
cognitive_brain:
  thresholds:
    severity_threshold: 0.8
    consecutive_threshold: 3
    confidence_threshold: 0.95
    per_workflow_overrides: {}
""".strip(),
        )
        proposer = ActionProposer(config_file=cfg)
        before = proposer.execute_action(
            {"action_type": "monitor", "workflow": "wf", "confidence": 0.9},
            dry_run=False,
        )
        assert before["status"] == "skipped", "bef is not valid"

        time.sleep(1.1)
        _write_config(
            cfg,
            """
cognitive_brain:
  thresholds:
    severity_threshold: 0.8
    consecutive_threshold: 3
    confidence_threshold: 0.8
    per_workflow_overrides: {}
""".strip(),
        )
        after = proposer.execute_action(
            {"action_type": "monitor", "workflow": "wf", "confidence": 0.9},
            dry_run=False,
        )
        assert after["status"] == "executed", "Condition must be true"


class TestSensorThresholdConfig:
    def test_should_propose_action_uses_defaults(self, tmp_path):
        workflows = {
            "wf_fail_0": {"last_status": "failure", "consecutive_failures": 7, "failure_rate": 1.0},
            "wf_fail_1": {"last_status": "failure", "consecutive_failures": 7, "failure_rate": 1.0},
            "wf_ok_0": {"last_status": "success"},
            "wf_ok_1": {"last_status": "success"},
            "wf_ok_2": {"last_status": "success"},
            "wf_ok_3": {"last_status": "success"},
            "wf_ok_4": {"last_status": "success"},
        }
        sensor = MonitoringSensor(
            state_file=_state_path(tmp_path, workflows),
            config_file=tmp_path / "missing.yaml",
        )
        should_act, _, confidence = sensor.should_propose_action()
        assert should_act is True, "should_act is not valid"
        assert confidence == 0.75, "confidence is not valid"

    def test_per_workflow_override_changes_decision(self, tmp_path):
        workflows = {
            "wf_fail_0": {"last_status": "failure", "consecutive_failures": 7, "failure_rate": 1.0},
            "wf_fail_1": {"last_status": "failure", "consecutive_failures": 7, "failure_rate": 1.0},
            "wf_ok_0": {"last_status": "success"},
            "wf_ok_1": {"last_status": "success"},
            "wf_ok_2": {"last_status": "success"},
            "wf_ok_3": {"last_status": "success"},
            "wf_ok_4": {"last_status": "success"},
        }
        cfg = tmp_path / "monitoring.yaml"
        _write_config(
            cfg,
            """
cognitive_brain:
  thresholds:
    severity_threshold: 0.8
    consecutive_threshold: 3
    confidence_threshold: 0.8
    per_workflow_overrides:
      wf_fail_0:
        severity_threshold: 0.9
      wf_fail_1:
        severity_threshold: 0.9
""".strip(),
        )
        sensor = MonitoringSensor(state_file=_state_path(tmp_path, workflows), config_file=cfg)
        should_act, _, confidence = sensor.should_propose_action()
        assert should_act is False, "should_act is not valid"
        assert confidence == 0.5, "confidence is not valid"
