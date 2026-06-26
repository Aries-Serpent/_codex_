"""Unit tests for src/codex_ml/continuous_learning/.

Coverage matrix (≥ 10 tests required):

 1.  should_retrain — score above threshold → True
 2.  should_retrain — score below threshold → False
 3.  should_retrain — drifted=True flag overrides score → True
 4.  should_retrain — drifted=False, score 0.0 → False
 5.  should_retrain — accepts object with .score attribute
 6.  trigger_retrain — returns RetrainingJob with correct fields
 7.  trigger_retrain — config snapshot stored in job and trigger
 8.  RetrainingTrigger.to_dict / from_dict round-trip
 9.  EvalGate — passes when all thresholds met
10.  EvalGate — fails when accuracy below min_accuracy
11.  EvalGate — fails when loss above max_loss
12.  EvalGate — fails when improvement below min_improvement_pct
13.  EvalGate — missing 'accuracy' key causes failure (not exception)
14.  EvalGate.evaluate returns EvalGateResult with passed/reasons/metrics
15.  promote — succeeds when eval gate passes (metrics provided)
16.  promote — blocked when eval gate fails (metrics provided)
17.  promote — updates registry in-place on success
18.  pipeline end-to-end with mocked drift result (dict form)
19.  pipeline end-to-end with mocked drift result (object form)
20.  RetrainingJob.to_dict serialisation
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from codex_ml.continuous_learning import (
    ContinuousLearningPipeline,
    EvalGate,
    EvalGateResult,
    RetrainingJob,
    RetrainingTrigger,
)

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


@dataclass
class _FakeDriftResult:
    """Minimal object mirroring DataDriftDetector's DriftResult interface."""

    score: float
    drifted: bool
    method: str = "psi"


def _make_pipeline(**kwargs) -> ContinuousLearningPipeline:
    defaults = dict(
        drift_threshold=0.2,
        eval_gate_min_accuracy=0.80,
        eval_gate_max_loss=0.5,
        eval_gate_min_improvement_pct=1.0,
    )
    defaults.update(kwargs)
    return ContinuousLearningPipeline(**defaults)


# ===========================================================================
# Tests 1–5: should_retrain
# ===========================================================================


class TestShouldRetrain:
    """Tests for ContinuousLearningPipeline.should_retrain."""

    # Test 1 — score above threshold
    def test_score_above_threshold_returns_true(self):
        pipeline = _make_pipeline(drift_threshold=0.2)
        assert pipeline.should_retrain({"score": 0.35}) is True, "Condition must be true"

    # Test 2 — score below threshold
    def test_score_below_threshold_returns_false(self):
        pipeline = _make_pipeline(drift_threshold=0.2)
        assert pipeline.should_retrain({"score": 0.10}) is False, "Condition must be true"

    # Test 3 — drifted=True overrides a zero score
    def test_drifted_flag_true_overrides_low_score(self):
        pipeline = _make_pipeline(drift_threshold=0.2)
        assert pipeline.should_retrain({"score": 0.05, "drifted": True}) is True

    # Test 4 — drifted=False, score 0 → no retrain
    def test_drifted_false_low_score_returns_false(self):
        pipeline = _make_pipeline(drift_threshold=0.2)
        assert pipeline.should_retrain({"score": 0.0, "drifted": False}) is False

    # Test 5 — accepts an object with .score / .drifted attributes
    def test_accepts_object_with_score_attribute(self):
        pipeline = _make_pipeline(drift_threshold=0.2)
        result = _FakeDriftResult(score=0.45, drifted=True)
        assert pipeline.should_retrain(result) is True, "Result must not be empty"

    def test_accepts_object_below_threshold(self):
        pipeline = _make_pipeline(drift_threshold=0.2)
        result = _FakeDriftResult(score=0.05, drifted=False)
        assert pipeline.should_retrain(result) is False, "Result must not be empty"

    def test_score_exactly_at_threshold_no_retrain(self):
        """score == threshold is NOT above threshold → no retrain."""
        pipeline = _make_pipeline(drift_threshold=0.2)
        assert pipeline.should_retrain({"score": 0.2}) is False, "Condition must be true"


# ===========================================================================
# Tests 6–8: trigger_retrain + RetrainingTrigger serialisation
# ===========================================================================


class TestTriggerRetrain:
    """Tests for ContinuousLearningPipeline.trigger_retrain and RetrainingTrigger."""

    # Test 6 — returns a properly formed RetrainingJob
    def test_trigger_retrain_returns_retraining_job(self):
        pipeline = _make_pipeline()
        job = pipeline.trigger_retrain()
        assert isinstance(job, RetrainingJob)
        assert isinstance(job.trigger, RetrainingTrigger)
        assert job.status == "pending", "status is not valid"
        assert job.job_id.startswith("retrain_"), "Condition must be true"

    # Test 7 — config snapshot propagated to job and trigger
    def test_config_snapshot_stored(self):
        pipeline = _make_pipeline()
        cfg = {"epochs": 10, "lr": 1e-4, "batch_size": 32}
        job = pipeline.trigger_retrain(cfg)
        assert job.config == cfg, "config is not valid"
        assert job.trigger.config_snapshot == cfg, "config_snapshot is not valid"

    # Test 8 — RetrainingTrigger round-trip serialisation
    def test_retraining_trigger_round_trip(self):
        ts = datetime(2024, 6, 1, 12, 0, 0, tzinfo=UTC)
        trigger = RetrainingTrigger(
            reason="data_drift_psi",
            drift_score=0.32,
            timestamp=ts,
            config_snapshot={"k": "v"},
        )
        d = trigger.to_dict()
        assert d["reason"] == "data_drift_psi", "Data must not be empty"
        assert d["drift_score"] == pytest.approx(0.32), "Condition must be true"
        assert "2024-06-01" in d["timestamp"], "Condition must be true"

        restored = RetrainingTrigger.from_dict(d)
        assert restored.reason == trigger.reason, "reason is not valid"
        assert restored.drift_score == pytest.approx(trigger.drift_score), "drift_score is not valid"
        assert restored.config_snapshot == trigger.config_snapshot, "config_snapshot is not valid"


# ===========================================================================
# Tests 9–14: EvalGate pass / fail scenarios
# ===========================================================================


class TestEvalGate:
    """Tests for EvalGate threshold checking."""

    # Test 9 — all thresholds met → passes
    def test_all_thresholds_met_passes(self):
        gate = EvalGate(min_accuracy=0.80, max_loss=0.5, min_improvement_pct=1.0)
        result = gate.evaluate({"accuracy": 0.85, "loss": 0.40, "baseline_accuracy": 0.83})
        assert result.passed is True, "Result must not be empty"
        assert result.reasons == [], "Result must not be empty"

    # Test 10 — accuracy below min_accuracy → fails
    def test_accuracy_below_minimum_fails(self):
        gate = EvalGate(min_accuracy=0.80)
        result = gate.evaluate({"accuracy": 0.75})
        assert result.passed is False, "Result must not be empty"
        assert any("min_accuracy" in r for r in result.reasons), "Result must not be empty"

    # Test 11 — loss above max_loss → fails
    def test_loss_above_maximum_fails(self):
        gate = EvalGate(max_loss=0.5)
        result = gate.evaluate({"loss": 0.75})
        assert result.passed is False, "Result must not be empty"
        assert any("max_loss" in r for r in result.reasons), "Result must not be empty"

    # Test 12 — improvement below min_improvement_pct → fails
    def test_insufficient_improvement_fails(self):
        gate = EvalGate(min_improvement_pct=5.0)
        # new=0.82, baseline=0.81 → improvement ~1.2% < 5%
        result = gate.evaluate({"accuracy": 0.82, "baseline_accuracy": 0.81})
        assert result.passed is False, "Result must not be empty"
        assert any("min_improvement_pct" in r for r in result.reasons), "Result must not be empty"

    # Test 13 — missing 'accuracy' key produces failure reason, not exception
    def test_missing_accuracy_key_produces_failure_reason(self):
        gate = EvalGate(min_accuracy=0.80)
        result = gate.evaluate({})
        assert result.passed is False, "Result must not be empty"
        assert any("missing" in r.lower() for r in result.reasons), "Result must not be empty"

    # Test 14 — result carries correct type and metrics snapshot
    def test_evaluate_returns_eval_gate_result(self):
        gate = EvalGate(min_accuracy=0.70)
        metrics = {"accuracy": 0.90, "loss": 0.20}
        result = gate.evaluate(metrics)
        assert isinstance(result, EvalGateResult)
        assert result.metrics == metrics, "Result must not be empty"
        assert result.passed is True, "Result must not be empty"

    def test_no_thresholds_configured_always_passes(self):
        """An EvalGate with no thresholds should pass any metrics."""
        gate = EvalGate()
        result = gate.evaluate({"accuracy": 0.0, "loss": 999.9})
        assert result.passed is True, "Result must not be empty"


# ===========================================================================
# Tests 15–17: promote
# ===========================================================================


class TestPromote:
    """Tests for ContinuousLearningPipeline.promote."""

    # Test 15 — promote succeeds with passing metrics
    def test_promote_succeeds_when_gate_passes(self):
        pipeline = _make_pipeline(
            eval_gate_min_accuracy=0.80,
            eval_gate_max_loss=0.5,
            eval_gate_min_improvement_pct=1.0,
        )
        registry: dict = {}
        result = pipeline.promote(
            "/models/v2.pt",
            registry,
            metrics={"accuracy": 0.88, "loss": 0.35, "baseline_accuracy": 0.83},
        )
        assert result is True, "Result must not be empty"

    # Test 16 — promote blocked when gate fails
    def test_promote_blocked_when_gate_fails(self):
        pipeline = _make_pipeline(eval_gate_min_accuracy=0.95)
        registry: dict = {}
        result = pipeline.promote(
            "/models/bad.pt",
            registry,
            metrics={"accuracy": 0.75},
        )
        assert result is False, "Result must not be empty"
        assert "model_path" not in registry, "Condition must be true"

    # Test 17 — registry updated in-place on success
    def test_registry_updated_on_success(self):
        pipeline = _make_pipeline(
            eval_gate_min_accuracy=0.80,
            eval_gate_max_loss=0.5,
            eval_gate_min_improvement_pct=1.0,
        )
        registry: dict = {}
        pipeline.promote(
            "/models/v3.pt",
            registry,
            metrics={"accuracy": 0.90, "loss": 0.35, "baseline_accuracy": 0.85},
        )
        assert registry["model_path"] == "/models/v3.pt", "Condition must be true"
        assert "promoted_at" in registry, "Condition must be true"

    def test_promote_without_metrics_always_succeeds(self):
        """Calling promote without metrics skips the gate check."""
        pipeline = _make_pipeline(eval_gate_min_accuracy=0.99)
        registry: dict = {}
        result = pipeline.promote("/models/v4.pt", registry)
        assert result is True, "Result must not be empty"
        assert registry["model_path"] == "/models/v4.pt", "Condition must be true"


# ===========================================================================
# Tests 18–19: end-to-end pipeline
# ===========================================================================


class TestPipelineEndToEnd:
    """End-to-end pipeline flow tests."""

    # Test 18 — dict-based drift result
    def test_end_to_end_with_dict_drift_result(self):
        pipeline = _make_pipeline(
            drift_threshold=0.2,
            eval_gate_min_accuracy=0.80,
        )
        drift_result = {"score": 0.35, "method": "psi", "drifted": True}

        assert pipeline.should_retrain(drift_result) is True, "Result must not be empty"
        job = pipeline.trigger_retrain({"epochs": 3, "lr": 5e-5})
        assert isinstance(job, RetrainingJob)

        metrics = {"accuracy": 0.86, "loss": 0.40, "baseline_accuracy": 0.82}
        registry: dict = {}
        promoted = pipeline.promote("/models/new.pt", registry, metrics=metrics)
        assert promoted is True, "promoted is not valid"
        assert registry["model_path"] == "/models/new.pt", "Condition must be true"
        assert pipeline.last_job is not None, "last_job must be initialized"
        assert pipeline.last_job.status == "done", "status is not valid"

    # Test 19 — object-based drift result (simulates DataDriftDetector output)
    def test_end_to_end_with_object_drift_result(self):
        pipeline = _make_pipeline(
            drift_threshold=0.1,
            eval_gate_min_accuracy=0.75,
            eval_gate_max_loss=None,
            eval_gate_min_improvement_pct=None,
        )
        fake_drift = _FakeDriftResult(score=0.55, drifted=True, method="kl")

        assert pipeline.should_retrain(fake_drift) is True, "Condition must be true"
        job = pipeline.trigger_retrain()
        assert job.trigger.reason == "drift_threshold_exceeded", "reason is not valid"

        metrics = {"accuracy": 0.80}
        assert pipeline.eval_gate(metrics) is True, "Condition must be true"

    # Test 20 — RetrainingJob.to_dict serialisation
    def test_retraining_job_to_dict(self):
        pipeline = _make_pipeline()
        job = pipeline.trigger_retrain({"param": "value"})
        d = job.to_dict()
        assert d["status"] == "pending", "Condition must be true"
        assert d["job_id"].startswith("retrain_"), "Condition must be true"
        assert "trigger" in d, "Condition must be true"
        assert d["config"] == {"param": "value"}, "Value must be initialized"

    def test_pipeline_last_trigger_populated_after_trigger_retrain(self):
        pipeline = _make_pipeline()
        assert pipeline.last_trigger is None, "last_trigger is not valid"
        pipeline.trigger_retrain()
        assert pipeline.last_trigger is not None, "last_trigger must be initialized"
        assert isinstance(pipeline.last_trigger, RetrainingTrigger)
