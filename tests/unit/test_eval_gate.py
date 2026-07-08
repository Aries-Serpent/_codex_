"""Unit tests for src/codex_ml/continuous_learning/eval_gate.py.

Tests cover:
  1.  EvalGateResult dataclass construction and to_dict serialisation
  2.  EvalGate with no thresholds always passes
  3.  min_accuracy threshold — pass (accuracy ≥ threshold)
  4.  min_accuracy threshold — fail (accuracy < threshold)
  5.  min_accuracy threshold — fail (accuracy key missing)
  6.  max_loss threshold — pass (loss ≤ threshold)
  7.  max_loss threshold — fail (loss > threshold)
  8.  max_loss threshold — fail (loss key missing)
  9.  min_improvement_pct — pass (improvement ≥ threshold)
  10. min_improvement_pct — fail (insufficient improvement)
  11. min_improvement_pct — fail (accuracy key missing)
  12. min_improvement_pct — fail (baseline_accuracy key missing)
  13. min_improvement_pct — fail (baseline_accuracy == 0)
  14. All thresholds combined — all pass
  15. All thresholds combined — multiple failures accumulated
  16. EvalGateResult.to_dict returns deep copy (metrics mutation does not bleed back)
  17. Boundary: accuracy exactly equal to min_accuracy passes
  18. Boundary: loss exactly equal to max_loss passes
  19. Boundary: improvement exactly equal to min_improvement_pct passes
  20. metrics dict stored in result is a shallow copy of the input
"""

from __future__ import annotations

from codex_ml.continuous_learning.eval_gate import EvalGate, EvalGateResult

# ---------------------------------------------------------------------------
# Test 1 — EvalGateResult construction and to_dict
# ---------------------------------------------------------------------------


class TestEvalGateResult:
    def test_default_fields(self):
        r = EvalGateResult(passed=True)
        assert r.passed is True, "passed is not valid"
        assert r.reasons == [], "reasons is not valid"
        assert r.metrics == {}, "metrics is not valid"

    def test_to_dict_structure(self):
        r = EvalGateResult(
            passed=False,
            reasons=["some reason"],
            metrics={"accuracy": 0.7},
        )
        d = r.to_dict()
        """Mutating the returned dict must not affect the original result."""
        r = EvalGateResult(passed=True, reasons=["x"], metrics={"a": 1})
        d = r.to_dict()
        d["reasons"].append("extra")
        d["metrics"]["b"] = 2
        assert r.reasons == ["x"], "reasons is not valid"
        assert r.metrics == {"a": 1}, "metrics is not valid"


# ---------------------------------------------------------------------------
# Test 2 — no thresholds
# ---------------------------------------------------------------------------


class TestEvalGateNoThresholds:
    def test_always_passes_empty_metrics(self):
        gate = EvalGate()
        result = gate.evaluate({})
        assert result.passed is True, "Result must not be empty"
        assert result.reasons == [], "Result must not be empty"

    def test_always_passes_with_metrics(self):
        gate = EvalGate()
        result = gate.evaluate({"accuracy": 0.5, "loss": 99.0})
        assert result.passed is True, "Result must not be empty"


# ---------------------------------------------------------------------------
# Tests 3-5 — min_accuracy
# ---------------------------------------------------------------------------


class TestMinAccuracy:
    def test_pass_accuracy_above_threshold(self):
        gate = EvalGate(min_accuracy=0.80)
        result = gate.evaluate({"accuracy": 0.85})
        assert result.passed is True, "Result must not be empty"
        assert result.reasons == [], "Result must not be empty"

    def test_fail_accuracy_below_threshold(self):
        gate = EvalGate(min_accuracy=0.80)
        result = gate.evaluate({"accuracy": 0.75})
        assert result.passed is False, "Result must not be empty"
        assert len(result.reasons) == 1, "Collection must not be empty"
        assert "min_accuracy=0.8" in result.reasons[0], "Result must not be empty"
        assert "accuracy=0.7500" in result.reasons[0], "Result must not be empty"

    def test_fail_accuracy_key_missing(self):
        gate = EvalGate(min_accuracy=0.80)
        result = gate.evaluate({"loss": 0.3})
        assert result.passed is False, "Result must not be empty"
        assert any("missing" in r for r in result.reasons), "Result must not be empty"

    def test_boundary_accuracy_exactly_threshold(self):
        gate = EvalGate(min_accuracy=0.80)
        result = gate.evaluate({"accuracy": 0.80})
        assert result.passed is True, "Result must not be empty"


# ---------------------------------------------------------------------------
# Tests 6-8 — max_loss
# ---------------------------------------------------------------------------


class TestMaxLoss:
    def test_pass_loss_below_threshold(self):
        gate = EvalGate(max_loss=0.5)
        result = gate.evaluate({"loss": 0.3})
        assert result.passed is True, "Result must not be empty"

    def test_fail_loss_above_threshold(self):
        gate = EvalGate(max_loss=0.5)
        result = gate.evaluate({"loss": 0.7})
        assert result.passed is False, "Result must not be empty"
        assert any("max_loss=0.5" in r for r in result.reasons), "Result must not be empty"
        assert any("loss=0.7000" in r for r in result.reasons), "Result must not be empty"

    def test_fail_loss_key_missing(self):
        gate = EvalGate(max_loss=0.5)
        result = gate.evaluate({"accuracy": 0.9})
        assert result.passed is False, "Result must not be empty"
        assert any("missing" in r for r in result.reasons), "Result must not be empty"

    def test_boundary_loss_exactly_threshold(self):
        gate = EvalGate(max_loss=0.5)
        result = gate.evaluate({"loss": 0.5})
        assert result.passed is True, "Result must not be empty"


# ---------------------------------------------------------------------------
# Tests 9-13 — min_improvement_pct
# ---------------------------------------------------------------------------


class TestMinImprovementPct:
    def test_pass_sufficient_improvement(self):
        # 0.83 → 0.85: (+0.02/0.83)*100 ≈ 2.41% > 1.0%
        gate = EvalGate(min_improvement_pct=1.0)
        result = gate.evaluate({"accuracy": 0.85, "baseline_accuracy": 0.83})
        assert result.passed is True, "Result must not be empty"

    def test_fail_insufficient_improvement(self):
        # 0.85 → 0.855: (+0.005/0.85)*100 ≈ 0.59% < 1.0%
        gate = EvalGate(min_improvement_pct=1.0)
        result = gate.evaluate({"accuracy": 0.855, "baseline_accuracy": 0.85})
        assert result.passed is False, "Result must not be empty"
        assert any("min_improvement_pct=1.0%" in r for r in result.reasons), "Result must not be empty"

    def test_fail_negative_improvement(self):
        # New model is worse than baseline
        gate = EvalGate(min_improvement_pct=1.0)
        result = gate.evaluate({"accuracy": 0.80, "baseline_accuracy": 0.85})
        assert result.passed is False, "Result must not be empty"

    def test_fail_accuracy_key_missing(self):
        gate = EvalGate(min_improvement_pct=1.0)
        result = gate.evaluate({"baseline_accuracy": 0.80})
        assert result.passed is False, "Result must not be empty"
        assert any("'accuracy' key missing" in r for r in result.reasons), "Result must not be empty"

    def test_fail_baseline_accuracy_key_missing(self):
        gate = EvalGate(min_improvement_pct=1.0)
        result = gate.evaluate({"accuracy": 0.85})
        assert result.passed is False, "Result must not be empty"
        assert any("'baseline_accuracy' key missing" in r for r in result.reasons), "Result must not be empty"

    def test_fail_baseline_accuracy_zero(self):
        gate = EvalGate(min_improvement_pct=1.0)
        result = gate.evaluate({"accuracy": 0.85, "baseline_accuracy": 0.0})
        assert result.passed is False, "Result must not be empty"
        assert any("must be > 0" in r for r in result.reasons), "be must be greater than zero"

    def test_boundary_improvement_exactly_threshold(self):
        # baseline=0.8, new=0.808 → improvement = (0.008/0.8)*100 = 1.0%
        gate = EvalGate(min_improvement_pct=1.0)
        result = gate.evaluate({"accuracy": 0.808, "baseline_accuracy": 0.8})
        assert result.passed is True, "Result must not be empty"


# ---------------------------------------------------------------------------
# Tests 14-15 — Combined thresholds
# ---------------------------------------------------------------------------


class TestCombinedThresholds:
    def test_all_thresholds_pass(self):
        gate = EvalGate(min_accuracy=0.80, max_loss=0.5, min_improvement_pct=1.0)
        metrics = {"accuracy": 0.85, "loss": 0.42, "baseline_accuracy": 0.83}
        result = gate.evaluate(metrics)
        assert result.passed is True, "Result must not be empty"
        assert result.reasons == [], "Result must not be empty"

    def test_multiple_failures_accumulated(self):
        gate = EvalGate(min_accuracy=0.90, max_loss=0.3, min_improvement_pct=5.0)
        # accuracy 0.80 < 0.90, loss 0.5 > 0.3, improvement ~2.4% < 5%
        metrics = {"accuracy": 0.80, "loss": 0.50, "baseline_accuracy": 0.78}
        result = gate.evaluate(metrics)
        assert result.passed is False, "Result must not be empty"
        assert len(result.reasons) == 3, "Collection must not be empty"

    def test_partial_failure_single_reason(self):
        gate = EvalGate(min_accuracy=0.90, max_loss=0.5)
        # accuracy fails, loss passes
        result = gate.evaluate({"accuracy": 0.80, "loss": 0.3})
        assert result.passed is False, "Result must not be empty"
        assert len(result.reasons) == 1, "Collection must not be empty"


# ---------------------------------------------------------------------------
# Test 16 — metrics stored in result is a copy of input
# ---------------------------------------------------------------------------


class TestMetricsCopy:
    def test_result_metrics_is_copy_of_input(self):
        gate = EvalGate()
        original = {"accuracy": 0.9, "loss": 0.1}
        result = gate.evaluate(original)
        original["accuracy"] = 0.0  # mutate original
        assert result.metrics["accuracy"] == 0.9, "Result must not be empty"

    def test_to_dict_metrics_copy(self):
        gate = EvalGate()
        result = gate.evaluate({"accuracy": 0.9})
        d = result.to_dict()
        d["metrics"]["accuracy"] = 0.0
        assert result.metrics["accuracy"] == 0.9, "Result must not be empty"


# ---------------------------------------------------------------------------
# Test — EvalGate stores configuration correctly
# ---------------------------------------------------------------------------


class TestEvalGateConfiguration:
    def test_attributes_stored(self):
        gate = EvalGate(min_accuracy=0.75, max_loss=1.0, min_improvement_pct=2.5)
        assert gate.min_accuracy == 0.75, "min_accuracy is not valid"
        assert gate.max_loss == 1.0, "max_loss is not valid"
        assert gate.min_improvement_pct == 2.5, "min_improvement_pct is not valid"

    def test_defaults_are_none(self):
        gate = EvalGate()
        assert gate.min_accuracy is None, "min_accuracy is not valid"
        assert gate.max_loss is None, "max_loss is not valid"
        assert gate.min_improvement_pct is None, "min_improvement_pct is not valid"
