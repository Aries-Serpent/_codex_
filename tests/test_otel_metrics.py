"""Tests for src/codex/monitoring/otel_metrics.py."""

from __future__ import annotations

import pytest

from codex.monitoring import Histogram, metrics
from codex.monitoring.otel_metrics import (
    compute_coherence,
    workflow_coherence_score,
    workflow_duration,
    workflow_step_duration,
)


class TestOtelMetricsModule:
    """Verify the pre-registered OTEL-style histogram instruments."""

    def test_workflow_duration_is_histogram(self) -> None:
        assert isinstance(workflow_duration, Histogram)

    def test_workflow_step_duration_is_histogram(self) -> None:
        assert isinstance(workflow_step_duration, Histogram)

    def test_workflow_coherence_score_is_histogram(self) -> None:
        assert isinstance(workflow_coherence_score, Histogram)

    def test_workflow_duration_name(self) -> None:
        assert workflow_duration.name == "workflow.job.duration", "name is not valid"

    def test_workflow_step_duration_name(self) -> None:
        assert workflow_step_duration.name == "workflow.step.duration", "name is not valid"

    def test_workflow_coherence_score_name(self) -> None:
        assert workflow_coherence_score.name == "workflow.coherence.score", "name is not valid"

    def test_workflow_duration_unit(self) -> None:
        assert workflow_duration.unit == "s", "unit is not valid"

    def test_workflow_step_duration_unit(self) -> None:
        assert workflow_step_duration.unit == "s", "unit is not valid"

    def test_workflow_coherence_score_unit(self) -> None:
        assert workflow_coherence_score.unit == "1", "unit is not valid"

    def test_workflow_duration_registered_in_registry(self) -> None:
        assert metrics.get("workflow.job.duration") is workflow_duration, "Condition must be true"

    def test_workflow_step_duration_registered_in_registry(self) -> None:
        assert metrics.get("workflow.step.duration") is workflow_step_duration, "Condition must be true"

    def test_workflow_coherence_score_registered_in_registry(self) -> None:
        assert metrics.get("workflow.coherence.score") is workflow_coherence_score, "Condition must be true"

    def test_observe_records_value(self) -> None:
        # Create a fresh histogram to avoid cross-test interference.
        h = Histogram(name="test.duration", description="test", unit="s")
        h.observe(1.5)
        h.observe(2.5)
        snap = h.snapshot()
        assert snap["count"] == 2, "Count must be greater than zero"
        assert abs(snap["sum"] - 4.0) < 1e-9, "Condition must be true"
        assert abs(snap["avg"] - 2.0) < 1e-9, "Condition must be true"

    def test_observe_empty_snapshot(self) -> None:
        h = Histogram(name="test.empty", description="test", unit="s")
        snap = h.snapshot()
        assert snap["count"] == 0, "Count must be greater than zero"
        assert snap["sum"] == 0.0, "Condition must be true"


class TestComputeCoherence:
    """Unit tests for the compute_coherence helper function."""

    def test_full_match_returns_one(self) -> None:
        actual = {"lint": "success", "test": "success", "build": "success"}
        expected = {"lint": "success", "test": "success", "build": "success"}
        assert compute_coherence(actual, expected) == 1.0

    def test_no_match_returns_zero(self) -> None:
        actual = {"lint": "failure", "test": "failure"}
        expected = {"lint": "success", "test": "success"}
        assert compute_coherence(actual, expected) == 0.0

    def test_partial_match(self) -> None:
        actual = {"lint": "success", "test": "failure"}
        expected = {"lint": "success", "test": "success"}
        assert compute_coherence(actual, expected) == pytest.approx(0.5)

    def test_empty_expected_returns_one(self) -> None:
        # Vacuously coherent — no constraints to violate.
        assert compute_coherence({"lint": "success"}, {}) == 1.0

    def test_extra_actual_steps_ignored(self) -> None:
        # Steps in actual but not expected do not affect the score.
        actual = {"lint": "success", "extra-step": "failure"}
        expected = {"lint": "success"}
        assert compute_coherence(actual, expected) == 1.0

    def test_missing_actual_step_is_mismatch(self) -> None:
        # A step expected by policy but absent from actual counts as failure.
        actual: dict[str, str] = {}
        expected = {"lint": "success"}
        assert compute_coherence(actual, expected) == 0.0

    def test_skipped_outcome_matches(self) -> None:
        actual = {"notify": "skipped"}
        expected = {"notify": "skipped"}
        assert compute_coherence(actual, expected) == 1.0

    def test_coherence_score_observable(self) -> None:
        # Verify the pre-registered histogram can record a coherence score.
        score = compute_coherence(
            {"lint": "success", "test": "success", "build": "failure"},
            {"lint": "success", "test": "success", "build": "success"},
        )
        # Score should be 2/3 ≈ 0.667
        assert abs(score - 2 / 3) < 1e-9, "Condition must be true"
        # Observation must not raise
        workflow_coherence_score.observe(score)
