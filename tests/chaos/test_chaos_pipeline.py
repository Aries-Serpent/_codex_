"""Chaos engineering tests for the ML pipeline components.

Exercises ContinuousLearningPipeline, FeedbackCollector, and ABTestSuite
under adverse conditions: repeated drift, corrupt configs, event overflow,
and degenerate A/B test inputs.
"""

from __future__ import annotations

from typing import Any

import pytest

from codex_ml.continuous_learning.pipeline import ContinuousLearningPipeline
from codex_ml.experiments.ab_testing import ABTestResult, run_ab_test
from codex_ml.feedback.collector import FeedbackCollector
from codex_ml.feedback.events import FeedbackEvent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_drift_result(drifted: bool, score: float) -> dict[str, Any]:
    return {"score": score, "drifted": drifted, "method": "psi"}


def _make_event(i: int) -> FeedbackEvent:
    return FeedbackEvent(
        event_type="metric",
        source=f"source_{i % 5}",
        payload={"value": i},
        score=float(i % 10),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestContinuousLearningUnderRepeatedDrift:
    """test_continuous_learning_under_repeated_drift"""

    def test_alternating_drift_triggers_then_backs_off(self) -> None:
        """Feed alternating drift/no-drift signals; pipeline triggers on drift
        and returns False on no-drift (backs off)."""
        pipeline = ContinuousLearningPipeline(drift_threshold=0.2)

        trigger_count = 0
        no_trigger_count = 0

        signals = [
            _make_drift_result(True, 0.5),  # drift
            _make_drift_result(False, 0.05),  # no drift
            _make_drift_result(True, 0.6),  # drift
            _make_drift_result(False, 0.1),  # no drift
            _make_drift_result(True, 0.9),  # drift
            _make_drift_result(False, 0.01),  # no drift
        ]

        for sig in signals:
            if pipeline.should_retrain(sig):
                trigger_count += 1
                pipeline.trigger_retrain({"epochs": 3})
            else:
                no_trigger_count += 1

        assert trigger_count == 3, f"expected 3 triggers, got {trigger_count}"
        assert no_trigger_count == 3, f"expected 3 no-triggers, got {no_trigger_count}"
        assert pipeline.last_job is not None, "last_job must be initialized"
        assert pipeline.last_trigger is not None, "last_trigger must be initialized"

    def test_high_score_always_triggers(self) -> None:
        """Scores far above threshold always trigger, regardless of drifted flag."""
        pipeline = ContinuousLearningPipeline(drift_threshold=0.1)
        for _ in range(10):
            result = pipeline.should_retrain({"score": 0.99, "drifted": False})
            assert result is True, "Result must not be empty"


class TestAutoRetrainWithCorruptConfig:
    """test_auto_retrain_with_corrupt_config"""

    def test_none_config_produces_valid_job(self) -> None:
        """None config should be tolerated and produce a valid RetrainingJob."""
        pipeline = ContinuousLearningPipeline()
        job = pipeline.trigger_retrain(config=None)
        assert job is not None, "job must be initialized"
        assert job.config == {}, "config is not valid"
        assert job.job_id.startswith("retrain_"), "Condition must be true"

    def test_empty_dict_config_accepted(self) -> None:
        """Empty dict config should be accepted."""
        pipeline = ContinuousLearningPipeline()
        job = pipeline.trigger_retrain(config={})
        assert isinstance(job.config, dict)

    def test_malformed_config_values_stored_verbatim(self) -> None:
        """Pipeline stores whatever config it receives — no exception."""
        weird_configs: list[dict[str, Any]] = [
            {"epochs": None},
            {"lr": float("inf")},
            {"batch": -1},
            {"nested": {"deep": {"deeper": "value"}}},
            {"\x00": "\xff"},  # non-printable keys
        ]
        pipeline = ContinuousLearningPipeline()
        for cfg in weird_configs:
            job = pipeline.trigger_retrain(config=cfg)
            assert job is not None, f"trigger_retrain should not raise for config={cfg!r}"

    def test_eval_gate_with_partial_metrics_returns_bool(self) -> None:
        """Eval gate with missing / partial metrics should not raise."""
        pipeline = ContinuousLearningPipeline(
            eval_gate_min_accuracy=0.8,
            eval_gate_max_loss=0.5,
        )
        partial_cases: list[dict[str, Any]] = [
            {},
            {"accuracy": 0.9},
            {"loss": 0.3},
            {"accuracy": None},  # type: ignore[dict-item]
            {"accuracy": "not_a_float"},  # type: ignore[dict-item]
        ]
        for metrics in partial_cases:
            try:
                result = pipeline.eval_gate(metrics)
                assert isinstance(result, bool), f"expected bool for metrics={metrics!r}"
            except (TypeError, ValueError):
                # Acceptable — partial / corrupt metrics may raise a typed error
                pass


class TestFeedbackLoopOverflow:
    """test_feedback_loop_overflow"""

    def test_get_recent_returns_exactly_100_after_overflow(self) -> None:
        """Record 1000+ events; get_recent(100) must return exactly 100."""
        collector = FeedbackCollector(max_memory=10_000)

        for i in range(1_050):
            collector.record(_make_event(i))

        recent = collector.get_recent(100)
        assert len(recent) == 100, f"expected 100, got {len(recent)}"
        # Most recent event should be last
        assert recent[-1].payload["value"] == 1049, "Value must be initialized"

    def test_aggregate_does_not_crash_with_large_buffer(self) -> None:
        """aggregate() must not raise after 1000 events are buffered."""
        collector = FeedbackCollector(max_memory=2_000)
        for i in range(1_000):
            collector.record(_make_event(i))

        summary = collector.aggregate()
        assert "total" in summary, "Condition must be true"
        assert summary["total"] == 1_000, "Condition must be true"
        assert "counts_by_type" in summary, "Count must be greater than zero"
        assert "avg_score" in summary, "Condition must be true"
        assert summary["avg_score"] is not None, "Value must be initialized"

    def test_ring_buffer_evicts_oldest_events(self) -> None:
        """When max_memory is exceeded, oldest events are dropped."""
        collector = FeedbackCollector(max_memory=100)
        for i in range(200):
            collector.record(_make_event(i))

        assert len(collector) == 100, "Collector must not be empty"
        events = collector.get_recent(100)
        # Oldest remaining event has payload value >= 100
        assert events[0].payload["value"] >= 100, "Value must be greater than zero"


class TestABTestingWithDegenerateInputs:
    """test_ab_testing_with_degenerate_inputs"""

    def test_single_element_groups_raises_value_error(self) -> None:
        """Single-element groups must raise ValueError (not crash uncontrolled)."""
        with pytest.raises(ValueError):
            run_ab_test([1.0], [2.0])

    def test_two_element_groups_runs_without_exception(self) -> None:
        """Minimum valid groups (2 elements each) must complete."""
        result = run_ab_test([1.0, 2.0], [3.0, 4.0])
        assert isinstance(result, ABTestResult)
        assert result.winner in {"control", "treatment", "inconclusive"}

    def test_all_equal_groups_returns_inconclusive(self) -> None:
        """All-equal control and treatment → p-value=1.0 → inconclusive."""
        ctrl = [5.0] * 50
        trt = [5.0] * 50
        result = run_ab_test(ctrl, trt)
        # With identical values, t-stat == 0 → high p-value → inconclusive
        assert result.winner == "inconclusive", "Result must not be empty"
        assert result.p_value == pytest.approx(1.0, abs=0.01)

    def test_extreme_outliers_do_not_crash(self) -> None:
        """Groups with extreme outlier values must complete without exception."""
        ctrl = [1.0, 2.0, 3.0] + [1e15]
        trt = [1.0, 2.0, 3.0, -1e15]
        result = run_ab_test(ctrl, trt)
        assert isinstance(result, ABTestResult)
        assert isinstance(result.p_value, float)
        assert isinstance(result.effect_size, float)
        lo, hi = result.confidence_interval
        assert isinstance(lo, float) and isinstance(hi, float)

    def test_large_equal_groups_produces_valid_shape(self) -> None:
        """Large (1000-element) equal-value groups: result shape is valid."""
        import random as _rnd

        rng = _rnd.Random(0)
        ctrl = [rng.gauss(0, 1) for _ in range(1000)]
        trt = [rng.gauss(0, 1) for _ in range(1000)]
        result = run_ab_test(ctrl, trt)
        assert result.winner in {"control", "treatment", "inconclusive"}
        lo, hi = result.confidence_interval
        assert lo <= hi, "CI lower bound must be <= upper bound"
