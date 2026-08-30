"""Unit tests for MonitoringSensor (scripts/cognitive/sensors/monitoring_sensor.py).

Phase 7 — Cognitive Brain Testing & Validation
Covers:
* get_system_health(): health score calculation, status classification, metrics
* get_active_failures(): filtering by consecutive_failures threshold, severity sort
* _calculate_severity(): formula validation, clamping
* should_propose_action(): all four decision branches
* export_state_for_cognitive_brain(): complete export structure
* Error resilience: missing / corrupt state file
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
_SENSOR_PATH = _REPO_ROOT / "scripts" / "cognitive" / "sensors" / "monitoring_sensor.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("monitoring_sensor", _SENSOR_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_mod = _load_module()
MonitoringSensor = _mod.MonitoringSensor

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_state(workflows: dict, last_run: str = "2026-01-22T07:00:00Z") -> dict:
    return {
        "workflows": workflows,
        "last_run": last_run,
        "metrics": {"total_runs": 100, "success_rate": 0.95},
    }


def _sensor(tmp_path: Path, state: dict | None = None) -> MonitoringSensor:
    state_file = tmp_path / "state.json"
    if state is not None:
        state_file.write_text(json.dumps(state))
    return MonitoringSensor(state_file=state_file)


# ---------------------------------------------------------------------------
# TestGetSystemHealth
# ---------------------------------------------------------------------------


class TestGetSystemHealth:
    def test_all_passing_workflows(self, tmp_path):
        """All workflows healthy → score=100, status='healthy'."""
        sensor = _sensor(
            tmp_path,
            _make_state({"wf_a": {"last_status": "success"}, "wf_b": {"last_status": "success"}}),
        )
        h = sensor.get_system_health()
        assert h["status"] == "healthy", "Condition must be true"
        assert h["health_score"] == 100.0, "Condition must be true"
        assert h["total_workflows"] == 2, "Condition must be true"
        assert h["failing_workflows"] == 0, "Condition must be true"

    def test_degraded_system(self, tmp_path):
        """25% failure rate → score=75 → 'degraded' (50 ≤ score < 80)."""
        workflows = {
            "wf_fail": {"last_status": "failure"},
            "wf_a": {"last_status": "success"},
            "wf_b": {"last_status": "success"},
            "wf_c": {"last_status": "success"},
        }
        sensor = _sensor(tmp_path, _make_state(workflows))
        h = sensor.get_system_health()
        assert h["status"] == "degraded", "Condition must be true"
        assert h["health_score"] == 75.0, "Condition must be true"
        assert h["failing_workflows"] == 1, "Condition must be true"

    def test_critical_system_all_failing(self, tmp_path):
        """All workflows failing → score=0 → 'critical' (score < 50)."""
        workflows = {f"wf_{i}": {"last_status": "failure"} for i in range(4)}
        sensor = _sensor(tmp_path, _make_state(workflows))
        h = sensor.get_system_health()
        assert h["status"] == "critical", "Condition must be true"
        assert h["health_score"] == 0.0, "Condition must be true"

    def test_critical_system_majority_failing(self, tmp_path):
        """3 failing out of 4 → 25% health → 'critical'."""
        workflows = {
            "wf_pass": {"last_status": "success"},
            "wf_f1": {"last_status": "failure"},
            "wf_f2": {"last_status": "failure"},
            "wf_f3": {"last_status": "failure"},
        }
        sensor = _sensor(tmp_path, _make_state(workflows))
        h = sensor.get_system_health()
        assert h["status"] == "critical", "Condition must be true"

    def test_empty_workflows_returns_100(self, tmp_path):
        """No workflows tracked → guard returns 100 (nothing to fail)."""
        sensor = _sensor(tmp_path, _make_state({}))
        h = sensor.get_system_health()
        assert h["status"] == "healthy", "Condition must be true"
        assert h["health_score"] == 100, "Condition must be true"

    def test_missing_state_file_is_resilient(self, tmp_path):
        """Non-existent state file → returns gracefully (no exception)."""
        sensor = MonitoringSensor(state_file=tmp_path / "nonexistent.json")
        h = sensor.get_system_health()
        # Either 'healthy' (empty state) or 'unknown' (error path) — both acceptable
        assert h["status"] in ("healthy", "unknown")

    def test_metrics_field_present(self, tmp_path):
        """Metrics block from state should be surfaced in result."""
        sensor = _sensor(tmp_path, _make_state({"wf_a": {"last_status": "success"}}))
        h = sensor.get_system_health()
        assert "metrics" in h, "Condition must be true"
        assert h["metrics"]["total_runs"] == 100, "Condition must be true"

    def test_last_check_field_present(self, tmp_path):
        sensor = _sensor(tmp_path, _make_state({"wf_a": {"last_status": "success"}}))
        h = sensor.get_system_health()
        assert h["last_check"] == "2026-01-22T07:00:00Z", "Condition must be true"

    def test_exactly_80_percent_is_healthy(self, tmp_path):
        """Edge: exactly 80% → status should be 'healthy' (score >= 80)."""
        workflows = {
            "wf_fail": {"last_status": "failure"},
            "wf_a": {"last_status": "success"},
            "wf_b": {"last_status": "success"},
            "wf_c": {"last_status": "success"},
            "wf_d": {"last_status": "success"},
        }
        sensor = _sensor(tmp_path, _make_state(workflows))
        h = sensor.get_system_health()
        assert h["health_score"] == 80.0, "Condition must be true"
        assert h["status"] == "healthy", "Condition must be true"

    def test_exactly_50_percent_is_degraded(self, tmp_path):
        """Edge: exactly 50% → status should be 'degraded' (score >= 50)."""
        workflows = {
            "wf_f1": {"last_status": "failure"},
            "wf_a": {"last_status": "success"},
        }
        sensor = _sensor(tmp_path, _make_state(workflows))
        h = sensor.get_system_health()
        assert h["health_score"] == 50.0, "Condition must be true"
        assert h["status"] == "degraded", "Condition must be true"


# ---------------------------------------------------------------------------
# TestGetActiveFailures
# ---------------------------------------------------------------------------


class TestGetActiveFailures:
    def test_no_failures_when_all_pass(self, tmp_path):
        sensor = _sensor(tmp_path, _make_state({"wf_a": {"last_status": "success"}}))
        assert sensor.get_active_failures() == [], "sens is not valid"

    def test_single_failure_consecutive_threshold(self, tmp_path):
        """consecutive_failures < 2 → not included in active failures."""
        workflows = {"wf_a": {"last_status": "failure", "consecutive_failures": 1}}
        sensor = _sensor(tmp_path, _make_state(workflows))
        assert sensor.get_active_failures() == [], "sens is not valid"

    def test_failure_at_consecutive_threshold(self, tmp_path):
        """consecutive_failures == 2 → included."""
        workflows = {
            "wf_a": {
                "last_status": "failure",
                "consecutive_failures": 2,
                "failure_rate": 0.4,
            }
        }
        sensor = _sensor(tmp_path, _make_state(workflows))
        failures = sensor.get_active_failures()
        assert len(failures) == 1, "Failures must not be empty"
        assert failures[0]["workflow"] == "wf_a", "Condition must be true"

    def test_failure_fields_present(self, tmp_path):
        """All expected fields included in failure dict."""
        workflows = {
            "wf_a": {
                "last_status": "failure",
                "consecutive_failures": 3,
                "failure_rate": 0.6,
                "last_failure": "2026-01-22T06:00:00Z",
                "open_issue_number": 99,
            }
        }
        sensor = _sensor(tmp_path, _make_state(workflows))
        failures = sensor.get_active_failures()
        f = failures[0]
        assert f["workflow"] == "wf_a", "Condition must be true"
        assert f["consecutive_failures"] == 3, "Condition must be true"
        assert f["failure_rate"] == 0.6, "Condition must be true"
        assert f["last_failure"] == "2026-01-22T06:00:00Z", "Condition must be true"
        assert f["open_issue"] == 99, "Condition must be true"
        assert "severity" in f, "Condition must be true"

    def test_failures_sorted_by_severity_descending(self, tmp_path):
        """Higher-severity failures come first."""
        workflows = {
            "wf_low": {
                "last_status": "failure",
                "consecutive_failures": 2,
                "failure_rate": 0.1,
            },
            "wf_high": {
                "last_status": "failure",
                "consecutive_failures": 9,
                "failure_rate": 0.95,
            },
        }
        sensor = _sensor(tmp_path, _make_state(workflows))
        failures = sensor.get_active_failures()
        assert len(failures) == 2, "Failures must not be empty"
        assert failures[0]["workflow"] == "wf_high", "Condition must be true"
        assert failures[0]["severity"] > failures[1]["severity"], "Value must be greater than zero"

    def test_passing_workflows_excluded(self, tmp_path):
        """Passing workflows not included even if high failure_rate metadata present."""
        workflows = {
            "wf_pass": {"last_status": "success", "consecutive_failures": 5},
            "wf_fail": {"last_status": "failure", "consecutive_failures": 3},
        }
        sensor = _sensor(tmp_path, _make_state(workflows))
        failures = sensor.get_active_failures()
        names = [f["workflow"] for f in failures]
        assert "wf_pass" not in names, "Condition must be true"

    def test_empty_state_returns_empty(self, tmp_path):
        sensor = _sensor(tmp_path, {})
        assert sensor.get_active_failures() == [], "sens is not valid"


# ---------------------------------------------------------------------------
# TestCalculateSeverity
# ---------------------------------------------------------------------------


class TestCalculateSeverity:
    @pytest.fixture
    def sensor(self, tmp_path):
        return MonitoringSensor(state_file=tmp_path / "s.json")

    def test_zero_inputs(self, sensor):
        assert sensor._calculate_severity({"consecutive_failures": 0, "failure_rate": 0}) == 0.0

    def test_formula_correctness(self, sensor):
        """Verify: (consecutive/10 * 0.6) + (failure_rate * 0.4)."""
        result = sensor._calculate_severity({"consecutive_failures": 5, "failure_rate": 0.5})
        expected = (5 / 10 * 0.6) + (0.5 * 0.4)
        assert abs(result - expected) < 1e-9, "Result must not be empty"

    def test_capped_at_one(self, sensor):
        result = sensor._calculate_severity({"consecutive_failures": 100, "failure_rate": 1.0})
        assert result == 1.0, "Result must not be empty"

    def test_defaults_when_keys_missing(self, sensor):
        """Missing keys default to 0 → severity = 0."""
        result = sensor._calculate_severity({})
        assert result == 0.0, "Result must not be empty"

    def test_high_consecutive_low_rate(self, sensor):
        result = sensor._calculate_severity({"consecutive_failures": 10, "failure_rate": 0.0})
        assert abs(result - 0.6) < 1e-9, "Result must not be empty"

    def test_low_consecutive_high_rate(self, sensor):
        result = sensor._calculate_severity({"consecutive_failures": 0, "failure_rate": 1.0})
        assert abs(result - 0.4) < 1e-9, "Result must not be empty"


# ---------------------------------------------------------------------------
# TestShouldProposeAction
# ---------------------------------------------------------------------------


class TestShouldProposeAction:
    def _sensor_with_workflows(self, tmp_path: Path, workflows: dict) -> MonitoringSensor:
        return _sensor(tmp_path, _make_state(workflows))

    def test_healthy_no_action(self, tmp_path):
        """100% healthy → (False, _, 0.3)."""
        sensor = self._sensor_with_workflows(
            tmp_path,
            {"wf_a": {"last_status": "success"}, "wf_b": {"last_status": "success"}},
        )
        should_act, reason, confidence = sensor.should_propose_action()
        assert should_act is False, "should_act is not valid"
        assert confidence == 0.3, "confidence is not valid"

    def test_critical_health_three_severe_failures(self, tmp_path):
        """health < 50 AND ≥3 critical failures → (True, _, 0.9)."""
        # 4 failing out of 5 = 20% health → critical
        # severity for each: (10/10*0.6)+(1.0*0.4)=1.0 ≥ 0.8 → 4 critical_failures
        workflows = {
            f"wf_f{i}": {"last_status": "failure", "consecutive_failures": 10, "failure_rate": 1.0}
            for i in range(4)
        }
        workflows["wf_ok"] = {"last_status": "success"}
        sensor = self._sensor_with_workflows(tmp_path, workflows)
        health = sensor.get_system_health()
        assert health["health_score"] < 50, "Condition must be true"
        should_act, reason, confidence = sensor.should_propose_action()
        assert should_act is True, "should_act is not valid"
        assert confidence == 0.9, "confidence is not valid"

    def test_degraded_health_two_critical_failures(self, tmp_path):
        """50 ≤ health < 80 AND ≥2 critical failures → (True, _, 0.75)."""
        # 2 failing out of 7 = 71.4% health → degraded
        # severity: (10/10*0.6)+(1.0*0.4)=1.0 ≥ 0.8 → 2 critical_failures
        workflows = {
            f"wf_f{i}": {"last_status": "failure", "consecutive_failures": 10, "failure_rate": 1.0}
            for i in range(2)
        }
        workflows.update({f"wf_ok{i}": {"last_status": "success"} for i in range(5)})
        sensor = self._sensor_with_workflows(tmp_path, workflows)
        health = sensor.get_system_health()
        assert 50 <= health["health_score"] < 80, "50 is not valid"
        should_act, reason, confidence = sensor.should_propose_action()
        assert should_act is True, "should_act is not valid"
        assert confidence == 0.75, "confidence is not valid"

    def test_degraded_no_critical_failures(self, tmp_path):
        """health < 80 BUT <2 critical failures → (False, _, 0.5)."""
        # 2 failing out of 5 = 60% health → degraded
        # severity: (2/10*0.6)+(0.2*0.4)=0.12+0.08=0.20 < 0.8 → 0 critical_failures
        workflows = {
            f"wf_f{i}": {"last_status": "failure", "consecutive_failures": 2, "failure_rate": 0.2}
            for i in range(2)
        }
        workflows.update({f"wf_ok{i}": {"last_status": "success"} for i in range(3)})
        sensor = self._sensor_with_workflows(tmp_path, workflows)
        health = sensor.get_system_health()
        assert 50 <= health["health_score"] < 80, "50 is not valid"
        should_act, reason, confidence = sensor.should_propose_action()
        assert should_act is False, "should_act is not valid"
        assert confidence == 0.5, "confidence is not valid"

    def test_reason_string_non_empty(self, tmp_path):
        """Every branch returns a non-empty reason string."""
        sensor = self._sensor_with_workflows(tmp_path, {"wf_a": {"last_status": "success"}})
        _, reason, _ = sensor.should_propose_action()
        assert isinstance(reason, str) and len(reason) > 0


# ---------------------------------------------------------------------------
# TestExportStateForCognitiveBrain
# ---------------------------------------------------------------------------


class TestExportStateForCognitiveBrain:
    def test_structure_keys_present(self, tmp_path):
        sensor = _sensor(tmp_path, {})
        export = sensor.export_state_for_cognitive_brain()
        assert export["sensor_type"] == "artifact_monitoring", "exp is not valid"
        assert "timestamp" in export, "Condition must be true"
        assert "system_health" in export, "Condition must be true"
        assert "active_failures" in export, "Condition must be true"
        assert "action_recommendation" in export, "Condition must be true"

    def test_action_recommendation_is_tuple_of_three(self, tmp_path):
        sensor = _sensor(tmp_path, {})
        export = sensor.export_state_for_cognitive_brain()
        rec = export["action_recommendation"]
        assert isinstance(rec, tuple)
        assert len(rec) == 3, "Rec must not be empty"
        should_act, reason, confidence = rec
        assert isinstance(should_act, bool)
        assert isinstance(reason, str)
        assert isinstance(confidence, float)

    def test_timestamp_is_iso_format(self, tmp_path):
        sensor = _sensor(tmp_path, {})
        export = sensor.export_state_for_cognitive_brain()
        ts = export["timestamp"]
        # ISO 8601 timestamps contain 'T' and 'Z' or '+00:00'
        assert "T" in ts, "Condition must be true"

    def test_active_failures_is_list(self, tmp_path):
        sensor = _sensor(tmp_path, {})
        export = sensor.export_state_for_cognitive_brain()
        assert isinstance(export["active_failures"], list)

    def test_system_health_is_dict(self, tmp_path):
        sensor = _sensor(tmp_path, {})
        export = sensor.export_state_for_cognitive_brain()
        assert isinstance(export["system_health"], dict)
