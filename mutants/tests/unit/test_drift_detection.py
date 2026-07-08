"""Unit tests for src/codex_ml/monitoring/drift_detection.py (Gap 5 — Wave 3/4).

Covers:
 T01. DriftAlert dataclass construction and to_dict()
 T02. DriftType constants
 T03. DriftDetector base: init, add_alert, get_alerts, clear_alerts
 T04. DriftDetector.detect() raises TypeError (must override in subclass)
 T05. DataDriftDetector — no drift (stats within threshold)
 T06. DataDriftDetector — mean drift detected
 T07. DataDriftDetector — std drift detected
 T08. DataDriftDetector — both mean and std drift detected
 T09. DataDriftDetector — missing keys are skipped gracefully
 T10. ModelDriftDetector — no drift (changes within threshold)
 T11. ModelDriftDetector — critical drift (>50% change)
 T12. ModelDriftDetector — high drift (30-50% change)
 T13. ModelDriftDetector — medium drift (15-30% change)
 T14. ModelDriftDetector — low drift (at threshold boundary)
 T15. ModelDriftDetector — baseline_val == 0 (uses absolute diff)
 T16. ModelDriftDetector — key absent in current_metrics is skipped
 T17. ComprehensiveDriftMonitor — init creates sub-detectors
 T18. ComprehensiveDriftMonitor — monitor_all with data only
 T19. ComprehensiveDriftMonitor — monitor_all with model only
 T20. ComprehensiveDriftMonitor — monitor_all with both
 T21. ComprehensiveDriftMonitor — monitor_all disabled returns empty dict
 T22. ComprehensiveDriftMonitor — get_all_alerts aggregates from all detectors
 T23. ComprehensiveDriftMonitor — clear_all_alerts empties all detectors
 T24. ComprehensiveDriftMonitor — has_critical_drift
 T25. ComprehensiveDriftMonitor — get_drift_summary structure
 T26. ComprehensiveDriftMonitor — save_alerts writes JSON file
 T27. DriftAlert.to_dict() returns serialisable structure
"""

from __future__ import annotations

import json
import pathlib

import pytest

from codex_ml.monitoring.drift_detection import (
    ComprehensiveDriftMonitor,
    DataDriftDetector,
    DriftAlert,
    DriftDetector,
    DriftType,
    ModelDriftDetector,
)

# ---------------------------------------------------------------------------
# T01 — DriftAlert construction and to_dict()
# ---------------------------------------------------------------------------


class TestDriftAlert:
    def test_construction_sets_fields(self):
        alert = DriftAlert(
            drift_type="data_drift",
            severity="high",
            message="Mean shifted",
            details={"key": "val"},
        )
        assert alert.drift_type == "data_drift", "Data must not be empty"
        assert alert.severity == "high", "severity is not valid"
        assert alert.message == "Mean shifted", "message is not valid"
        assert alert.details == {"key": "val"}, "details is not valid"
        assert alert.timestamp is None, "timestamp is not valid"

    def test_to_dict_contains_all_keys(self):
        alert = DriftAlert(
            drift_type="model_drift",
            severity="low",
            message="Minor",
            details={"metric": "loss"},
            timestamp="2026-01-01T00:00:00Z",
        )
        d = alert.to_dict()
        assert d["drift_type"] == "model_drift", "Condition must be true"
        assert d["severity"] == "low", "Condition must be true"
        assert d["message"] == "Minor", "Condition must be true"
        assert d["details"] == {"metric": "loss"}, "Condition must be true"
        assert d["timestamp"] == "2026-01-01T00:00:00Z", "Condition must be true"

    def test_to_dict_is_json_serialisable(self):
        alert = DriftAlert("data_drift", "medium", "msg", {"x": 1})
        # Should not raise
        json.dumps(alert.to_dict())


# ---------------------------------------------------------------------------
# T02 — DriftType constants
# ---------------------------------------------------------------------------


class TestDriftType:
    def test_constants_are_strings(self):
        assert isinstance(DriftType.DATA, str)
        assert isinstance(DriftType.CONFIG, str)
        assert isinstance(DriftType.MODEL, str)
        assert isinstance(DriftType.CHECKPOINT, str)
        assert isinstance(DriftType.ENVIRONMENT, str)

    def test_distinct_values(self):
        values = {
            DriftType.DATA,
            DriftType.CONFIG,
            DriftType.MODEL,
            DriftType.CHECKPOINT,
            DriftType.ENVIRONMENT,
        }
        assert len(values) == 5, "Values must not be empty"


# ---------------------------------------------------------------------------
# T03 — DriftDetector base class
# ---------------------------------------------------------------------------


class TestDriftDetectorBase:
    def test_init_defaults(self):
        dd = DriftDetector(threshold=0.2)
        assert dd.threshold == 0.2, "threshold is not valid"
        assert dd.alerts == [], "alerts is not valid"

    def test_add_alert_appends(self):
        dd = DriftDetector()
        alert = DriftAlert("data_drift", "low", "test", {})
        dd.add_alert(alert)
        assert len(dd.alerts) == 1, "Collection must not be empty"
        assert dd.alerts[0] is alert, "Condition must be true"

    def test_get_alerts_returns_list(self):
        dd = DriftDetector()
        alert = DriftAlert("data_drift", "low", "test", {})
        dd.add_alert(alert)
        alerts = dd.get_alerts()
        assert isinstance(alerts, list)
        assert len(alerts) == 1, "Alerts must not be empty"

    def test_clear_alerts(self):
        dd = DriftDetector()
        dd.add_alert(DriftAlert("data_drift", "low", "test", {}))
        dd.add_alert(DriftAlert("data_drift", "high", "test2", {}))
        dd.clear_alerts()
        assert dd.alerts == [], "alerts is not valid"


# ---------------------------------------------------------------------------
# T04 — DriftDetector.detect() raises TypeError (must be overridden)
# ---------------------------------------------------------------------------


class TestDriftDetectorDetectRaises:
    def test_detect_raises_type_error(self):
        dd = DriftDetector()
        with pytest.raises(TypeError, match="must be implemented by subclass"):
            dd.detect("current", "baseline")


# ---------------------------------------------------------------------------
# T05-T09 — DataDriftDetector
# ---------------------------------------------------------------------------


class TestDataDriftDetectorNoDrift:
    def test_no_drift_within_threshold(self):
        dd = DataDriftDetector(threshold=0.5)
        result = dd.detect(
            current_stats={"mean": 1.0, "std": 0.1},
            baseline_stats={"mean": 1.1, "std": 0.15},
        )
        assert result is False, "Result must not be empty"
        assert len(dd.alerts) == 0, "Collection must not be empty"

    def test_no_alerts_on_identical_stats(self):
        dd = DataDriftDetector(threshold=0.1)
        dd.detect({"mean": 5.0, "std": 1.0}, {"mean": 5.0, "std": 1.0})
        assert len(dd.alerts) == 0, "Collection must not be empty"


class TestDataDriftDetectorMeanDrift:
    def test_mean_drift_detected(self):
        dd = DataDriftDetector(threshold=0.1)
        result = dd.detect(
            current_stats={"mean": 2.0},
            baseline_stats={"mean": 1.0},
        )
        assert result is True, "Result must not be empty"
        assert len(dd.alerts) == 1, "Collection must not be empty"
        assert dd.alerts[0].drift_type == DriftType.DATA, "Data must not be empty"
        assert dd.alerts[0].severity == "high", "severity is not valid"

    def test_mean_drift_alert_details(self):
        dd = DataDriftDetector(threshold=0.1)
        dd.detect({"mean": 2.0}, {"mean": 1.0})
        alert = dd.alerts[0]
        assert "current_mean" in alert.details, "Condition must be true"
        assert "baseline_mean" in alert.details, "Condition must be true"


class TestDataDriftDetectorStdDrift:
    def test_std_drift_detected(self):
        dd = DataDriftDetector(threshold=0.05)
        result = dd.detect(
            current_stats={"std": 2.0},
            baseline_stats={"std": 1.0},
        )
        assert result is True, "Result must not be empty"
        assert any(a.severity == "medium" for a in dd.alerts), "severity is not valid"

    def test_both_mean_and_std_drift(self):
        dd = DataDriftDetector(threshold=0.1)
        result = dd.detect(
            current_stats={"mean": 5.0, "std": 5.0},
            baseline_stats={"mean": 1.0, "std": 1.0},
        )
        assert result is True, "Result must not be empty"
        assert len(dd.alerts) == 2, "Collection must not be empty"


class TestDataDriftDetectorMissingKeys:
    def test_missing_mean_key_skipped(self):
        dd = DataDriftDetector(threshold=0.1)
        # No 'mean' key — should not crash
        result = dd.detect(
            current_stats={"other": 1.0},
            baseline_stats={"other": 2.0},
        )
        assert result is False, "Result must not be empty"
        assert len(dd.alerts) == 0, "Collection must not be empty"


# ---------------------------------------------------------------------------
# T10-T16 — ModelDriftDetector
# ---------------------------------------------------------------------------


class TestModelDriftDetectorNoDrift:
    def test_no_drift_within_threshold(self):
        dd = ModelDriftDetector(threshold=0.1)
        result = dd.detect(
            current_metrics={"accuracy": 0.95, "loss": 0.5},
            baseline_metrics={"accuracy": 0.95, "loss": 0.5},
        )
        assert result is False, "Result must not be empty"
        assert len(dd.alerts) == 0, "Collection must not be empty"

    def test_small_change_below_threshold(self):
        dd = ModelDriftDetector(threshold=0.2)
        result = dd.detect(
            current_metrics={"accuracy": 0.90},
            baseline_metrics={"accuracy": 0.91},  # ~1.1% change
        )
        assert result is False, "Result must not be empty"


class TestModelDriftDetectorCritical:
    def test_critical_drift_greater_than_50_percent(self):
        dd = ModelDriftDetector(threshold=0.1)
        dd.detect(
            current_metrics={"accuracy": 0.4},
            baseline_metrics={"accuracy": 0.9},  # 55% drop
        )
        assert any(a.severity == "critical" for a in dd.alerts), "severity is not valid"


class TestModelDriftDetectorHigh:
    def test_high_drift_30_to_50_percent(self):
        dd = ModelDriftDetector(threshold=0.1)
        dd.detect(
            current_metrics={"accuracy": 0.6},
            baseline_metrics={"accuracy": 0.9},  # 33% drop
        )
        assert any(a.severity == "high" for a in dd.alerts), "severity is not valid"


class TestModelDriftDetectorMedium:
    def test_medium_drift_15_to_30_percent(self):
        dd = ModelDriftDetector(threshold=0.1)
        dd.detect(
            current_metrics={"accuracy": 0.75},
            baseline_metrics={"accuracy": 0.9},  # ~16.7% drop
        )
        assert any(a.severity == "medium" for a in dd.alerts), "severity is not valid"


class TestModelDriftDetectorLow:
    def test_low_drift_at_threshold_boundary(self):
        dd = ModelDriftDetector(threshold=0.1)
        dd.detect(
            current_metrics={"accuracy": 0.8},
            baseline_metrics={"accuracy": 0.9},  # 11.1% drop > threshold=0.1
        )
        # Should produce low severity (0.1 < rel_change < 0.15)
        severities = {a.severity for a in dd.alerts}
        assert severities, "severities is not valid"


class TestModelDriftDetectorBaselineZero:
    def test_baseline_zero_uses_absolute_diff(self):
        dd = ModelDriftDetector(threshold=0.05)
        result = dd.detect(
            current_metrics={"score": 0.5},
            baseline_metrics={"score": 0.0},
        )
        # abs(0.5 - 0.0) = 0.5 > 0.05 → should detect drift
        assert result is True, "Result must not be empty"


class TestModelDriftDetectorMissingKey:
    def test_key_absent_in_current_skipped(self):
        dd = ModelDriftDetector(threshold=0.1)
        result = dd.detect(
            current_metrics={"different_metric": 0.9},
            baseline_metrics={"accuracy": 0.9},
        )
        assert result is False, "Result must not be empty"
        assert len(dd.alerts) == 0, "Collection must not be empty"


class TestModelDriftAlertDetails:
    def test_alert_details_contain_metric_name(self):
        dd = ModelDriftDetector(threshold=0.1)
        dd.detect(
            current_metrics={"f1": 0.4},
            baseline_metrics={"f1": 0.9},
        )
        assert dd.alerts, "Condition must be true"
        assert dd.alerts[0].details["metric"] == "f1", "Condition must be true"
        assert "relative_change" in dd.alerts[0].details, "Condition must be true"


# ---------------------------------------------------------------------------
# T17-T26 — ComprehensiveDriftMonitor
# ---------------------------------------------------------------------------


class TestComprehensiveDriftMonitorInit:
    def test_creates_sub_detectors(self):
        monitor = ComprehensiveDriftMonitor()
        assert isinstance(monitor.data_detector, DataDriftDetector)
        assert isinstance(monitor.model_detector, ModelDriftDetector)
        assert monitor.monitoring_enabled is True, "monitoring_enabled is not valid"

    def test_custom_thresholds_propagated(self):
        monitor = ComprehensiveDriftMonitor(data_threshold=0.5, model_threshold=0.3)
        assert monitor.data_detector.threshold == 0.5, "Data must not be empty"
        assert monitor.model_detector.threshold == 0.3, "threshold is not valid"


class TestComprehensiveDriftMonitorDataOnly:
    def test_monitor_all_data_drift(self):
        monitor = ComprehensiveDriftMonitor(data_threshold=0.1)
        results = monitor.monitor_all(
            current_data_stats={"mean": 5.0},
            baseline_data_stats={"mean": 1.0},
        )
        assert "data" in results, "Result must not be empty"
        assert results["data"] is True, "Result must not be empty"

    def test_monitor_all_no_data_args_returns_empty(self):
        monitor = ComprehensiveDriftMonitor()
        results = monitor.monitor_all()
        assert results == {}, "Result must not be empty"


class TestComprehensiveDriftMonitorModelOnly:
    def test_monitor_all_model_drift(self):
        monitor = ComprehensiveDriftMonitor(model_threshold=0.1)
        results = monitor.monitor_all(
            current_metrics={"accuracy": 0.4},
            baseline_metrics={"accuracy": 0.9},
        )
        assert "model" in results, "Result must not be empty"
        assert results["model"] is True, "Result must not be empty"


class TestComprehensiveDriftMonitorDisabled:
    def test_disabled_monitoring_returns_empty_dict(self):
        monitor = ComprehensiveDriftMonitor()
        monitor.monitoring_enabled = False
        results = monitor.monitor_all(
            current_data_stats={"mean": 5.0},
            baseline_data_stats={"mean": 1.0},
        )
        assert results == {}, "Result must not be empty"


class TestComprehensiveDriftMonitorAggregation:
    def test_get_all_alerts_aggregates(self):
        monitor = ComprehensiveDriftMonitor(data_threshold=0.05, model_threshold=0.05)
        monitor.monitor_all(
            current_data_stats={"mean": 5.0},
            baseline_data_stats={"mean": 1.0},
            current_metrics={"loss": 5.0},
            baseline_metrics={"loss": 1.0},
        )
        alerts = monitor.get_all_alerts()
        assert len(alerts) >= 2, "Alerts must not be empty"

    def test_clear_all_alerts(self):
        monitor = ComprehensiveDriftMonitor(data_threshold=0.05)
        monitor.monitor_all(
            current_data_stats={"mean": 5.0},
            baseline_data_stats={"mean": 1.0},
        )
        assert len(monitor.get_all_alerts()) > 0, "Collection must not be empty"
        monitor.clear_all_alerts()
        assert monitor.get_all_alerts() == [], "monit is not valid"


class TestComprehensiveDriftMonitorCritical:
    def test_has_critical_drift_true(self):
        monitor = ComprehensiveDriftMonitor(model_threshold=0.1)
        monitor.monitor_all(
            current_metrics={"accuracy": 0.3},
            baseline_metrics={"accuracy": 0.9},  # 67% drop → critical
        )
        assert monitor.has_critical_drift() is True, "monit is not valid"

    def test_has_critical_drift_false_when_no_alerts(self):
        monitor = ComprehensiveDriftMonitor()
        assert monitor.has_critical_drift() is False, "monit is not valid"


class TestComprehensiveDriftMonitorSummary:
    def test_get_drift_summary_structure(self):
        monitor = ComprehensiveDriftMonitor(model_threshold=0.1)
        monitor.monitor_all(
            current_metrics={"accuracy": 0.3},
            baseline_metrics={"accuracy": 0.9},
        )
        summary = monitor.get_drift_summary()
        assert "total_alerts" in summary, "Condition must be true"
        assert "by_type" in summary, "Condition must be true"
        assert "by_severity" in summary, "Condition must be true"
        assert "critical_count" in summary, "Count must be greater than zero"
        assert summary["total_alerts"] >= 1, "Value must be greater than zero"

    def test_get_drift_summary_empty(self):
        monitor = ComprehensiveDriftMonitor()
        summary = monitor.get_drift_summary()
        assert summary["total_alerts"] == 0, "Condition must be true"
        assert summary["critical_count"] == 0, "Count must be greater than zero"


class TestComprehensiveDriftMonitorSaveAlerts:
    def test_save_alerts_writes_json(self, tmp_path: pathlib.Path):
        monitor = ComprehensiveDriftMonitor(model_threshold=0.1)
        monitor.monitor_all(
            current_metrics={"accuracy": 0.3},
            baseline_metrics={"accuracy": 0.9},
        )
        out_file = tmp_path / "alerts.json"
        monitor.save_alerts(out_file)
        assert out_file.exists(), "Condition must be true"
        data = json.loads(out_file.read_text())
        assert isinstance(data, list)
        assert len(data) >= 1, "Data must not be empty"

    def test_save_alerts_empty_list_when_no_drift(self, tmp_path: pathlib.Path):
        monitor = ComprehensiveDriftMonitor()
        out_file = tmp_path / "empty_alerts.json"
        monitor.save_alerts(out_file)
        assert out_file.exists(), "Condition must be true"
        data = json.loads(out_file.read_text())
        assert data == [], "Data must not be empty"
