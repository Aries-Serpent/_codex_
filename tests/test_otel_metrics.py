"""Tests for src/codex/monitoring/otel_metrics.py."""
from __future__ import annotations

from codex.monitoring import Histogram, metrics
from codex.monitoring.otel_metrics import workflow_duration, workflow_step_duration


class TestOtelMetricsModule:
    """Verify the pre-registered OTEL-style histogram instruments."""

    def test_workflow_duration_is_histogram(self) -> None:
        assert isinstance(workflow_duration, Histogram)

    def test_workflow_step_duration_is_histogram(self) -> None:
        assert isinstance(workflow_step_duration, Histogram)

    def test_workflow_duration_name(self) -> None:
        assert workflow_duration.name == "workflow.job.duration"

    def test_workflow_step_duration_name(self) -> None:
        assert workflow_step_duration.name == "workflow.step.duration"

    def test_workflow_duration_unit(self) -> None:
        assert workflow_duration.unit == "s"

    def test_workflow_step_duration_unit(self) -> None:
        assert workflow_step_duration.unit == "s"

    def test_workflow_duration_registered_in_registry(self) -> None:
        assert metrics.get("workflow.job.duration") is workflow_duration

    def test_workflow_step_duration_registered_in_registry(self) -> None:
        assert metrics.get("workflow.step.duration") is workflow_step_duration

    def test_observe_records_value(self) -> None:
        # Create a fresh histogram to avoid cross-test interference.
        h = Histogram(name="test.duration", description="test", unit="s")
        h.observe(1.5)
        h.observe(2.5)
        snap = h.snapshot()
        assert snap["count"] == 2
        assert abs(snap["sum"] - 4.0) < 1e-9
        assert abs(snap["avg"] - 2.0) < 1e-9

    def test_observe_empty_snapshot(self) -> None:
        h = Histogram(name="test.empty", description="test", unit="s")
        snap = h.snapshot()
        assert snap["count"] == 0
        assert snap["sum"] == 0.0
