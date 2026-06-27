"""Unit tests for src/codex_ml/experiments/ab_testing.py.

Tests cover:
  1. Significant difference detection — clearly different groups → winner ≠ inconclusive
  2. Inconclusive result — nearly identical groups → winner == "inconclusive"
  3. Effect size calculation — large vs small Cohen's d
  4. Confidence interval bounds — CI excludes zero for significant result
  5. CI straddles zero for inconclusive result
  6. Suite report structure — keys, counts, nested test dict
  7. Alpha threshold sensitivity — tighter alpha makes more tests inconclusive
  8. Treatment winner — treatment mean > control mean
  9. Control winner — control mean > treatment mean
 10. ABTest dataclass validation — invalid alpha raises ValueError
"""

from __future__ import annotations

import math

import pytest

from codex_ml.experiments import ABTest, ABTestSuite, run_ab_test

# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

# Clearly different groups: control ~10, treatment ~20
_CTRL_HIGH_DIFF = [10.0, 10.1, 9.9, 10.05, 9.95, 10.2, 9.8, 10.15, 9.85, 10.0]
_TRT_HIGH_DIFF = [20.0, 20.1, 19.9, 20.05, 19.95, 20.2, 19.8, 20.15, 19.85, 20.0]

# Nearly identical groups: control ≈ treatment ≈ 5
_CTRL_NO_DIFF = [5.0, 5.01, 4.99, 5.0, 5.02, 4.98, 5.01, 4.99, 5.0, 5.0]
_TRT_NO_DIFF = [5.0, 5.01, 4.99, 5.0, 5.02, 4.98, 5.01, 4.99, 5.0, 5.0]


# ---------------------------------------------------------------------------
# Test 1 — Significant difference detection
# ---------------------------------------------------------------------------


class TestSignificantDifference:
    """Clearly different groups must produce significant=True."""

    def test_significant_flag_is_true(self):
        result = run_ab_test(_CTRL_HIGH_DIFF, _TRT_HIGH_DIFF)
        assert result.significant is True, "Result must not be empty"

    def test_winner_is_not_inconclusive(self):
        result = run_ab_test(_CTRL_HIGH_DIFF, _TRT_HIGH_DIFF)
        assert result.winner != "inconclusive", "Result must not be empty"

    def test_p_value_below_alpha(self):
        result = run_ab_test(_CTRL_HIGH_DIFF, _TRT_HIGH_DIFF, alpha=0.05)
        assert result.p_value < 0.05, "Result must not be empty"


# ---------------------------------------------------------------------------
# Test 2 — Inconclusive result
# ---------------------------------------------------------------------------


class TestInconclusiveResult:
    """Identical groups must produce winner == 'inconclusive'."""

    def test_winner_inconclusive(self):
        result = run_ab_test(_CTRL_NO_DIFF, _TRT_NO_DIFF)
        assert result.winner == "inconclusive", "Result must not be empty"

    def test_significant_flag_is_false(self):
        result = run_ab_test(_CTRL_NO_DIFF, _TRT_NO_DIFF)
        assert result.significant is False, "Result must not be empty"

    def test_p_value_high(self):
        result = run_ab_test(_CTRL_NO_DIFF, _TRT_NO_DIFF)
        # identical → p_value should be exactly 1 (or very close to it)
        assert result.p_value > 0.9, "p_value must be greater than zero"


# ---------------------------------------------------------------------------
# Test 3 — Effect size calculation
# ---------------------------------------------------------------------------


class TestEffectSize:
    """Cohen's d should be large for well-separated groups."""

    def test_large_effect_size_for_different_groups(self):
        result = run_ab_test(_CTRL_HIGH_DIFF, _TRT_HIGH_DIFF)
        assert (abs(result.effect_size) > 5.0, "Value must be greater than zero"
        ), f"Expected large Cohen's d for well-separated groups, got {result.effect_size}"

    def test_zero_effect_size_for_identical_groups(self):
        result = run_ab_test(_CTRL_NO_DIFF, _TRT_NO_DIFF)
        assert math.isclose(result.effect_size, 0.0, abs_tol=1e-9)

    def test_effect_size_type_is_float(self):
        result = run_ab_test(_CTRL_HIGH_DIFF, _TRT_HIGH_DIFF)
        assert isinstance(result.effect_size, float)


# ---------------------------------------------------------------------------
# Test 4 — Confidence interval excludes zero (significant result)
# ---------------------------------------------------------------------------


class TestConfidenceIntervalSignificant:
    """For a significant result, the CI of the mean difference must not span 0."""

    def test_ci_excludes_zero(self):
        result = run_ab_test(_CTRL_HIGH_DIFF, _TRT_HIGH_DIFF)
        ci_lo, ci_hi = result.confidence_interval
        # both bounds should be positive (treatment - control ≈ +10)
        assert ci_lo > 0.0, f"CI lower bound {ci_lo} should be > 0"
        assert ci_hi > 0.0, f"CI upper bound {ci_hi} should be > 0"

    def test_ci_is_ordered(self):
        result = run_ab_test(_CTRL_HIGH_DIFF, _TRT_HIGH_DIFF)
        assert result.confidence_interval[0] < result.confidence_interval[1], "Result must not be empty"

    def test_ci_contains_true_difference(self):
        """True difference is ≈10; CI should contain it."""
        result = run_ab_test(_CTRL_HIGH_DIFF, _TRT_HIGH_DIFF)
        ci_lo, ci_hi = result.confidence_interval
        assert ci_lo <= 10.0 <= ci_hi, "ci_lo is not valid"


# ---------------------------------------------------------------------------
# Test 5 — Confidence interval straddles zero (inconclusive result)
# ---------------------------------------------------------------------------


class TestConfidenceIntervalInconclusive:
    """For identical groups the CI of the mean difference should span 0."""

    def test_ci_straddles_zero(self):
        result = run_ab_test(_CTRL_NO_DIFF, _TRT_NO_DIFF)
        ci_lo, ci_hi = result.confidence_interval
        assert (ci_lo <= 0.0 <= ci_hi, "ci_lo is not valid"
        ), f"Expected CI to straddle 0 for identical groups, got [{ci_lo}, {ci_hi}]"


# ---------------------------------------------------------------------------
# Test 6 — Suite report structure
# ---------------------------------------------------------------------------


class TestSuiteReportStructure:
    """ABTestSuite.report() must return a well-formed dict."""

    def _build_suite(self) -> ABTestSuite:
        suite = ABTestSuite()
        suite.add_test(ABTest("click_rate", _CTRL_HIGH_DIFF, _TRT_HIGH_DIFF))
        suite.add_test(ABTest("revenue", _CTRL_NO_DIFF, _TRT_NO_DIFF))
        return suite

    def test_report_has_summary_key(self):
        report = self._build_suite().report()
        assert "summary" in report, "Condition must be true"

    def test_report_summary_has_required_keys(self):
        report = self._build_suite().report()
        assert {"total", "significant", "inconclusive"} == set(report["summary"].keys())

    def test_report_total_count(self):
        report = self._build_suite().report()
        assert report["summary"]["total"] == 2, "rep is not valid"

    def test_report_has_tests_key(self):
        report = self._build_suite().report()
        assert "tests" in report, "Condition must be true"

    def test_report_tests_contains_registered_names(self):
        report = self._build_suite().report()
        assert "click_rate" in report["tests"], "Condition must be true"
        assert "revenue" in report["tests"], "Condition must be true"

    def test_report_test_entry_has_required_keys(self):
        report = self._build_suite().report()
        entry = report["tests"]["click_rate"]
        required = {"winner", "p_value", "effect_size", "confidence_interval", "significant"}
        assert required.issubset(entry.keys()), "Condition must be true"

    def test_report_significant_count(self):
        report = self._build_suite().report()
        # click_rate should be significant, revenue should not
        assert report["summary"]["significant"] == 1, "rep is not valid"
        assert report["summary"]["inconclusive"] == 1, "rep is not valid"


# ---------------------------------------------------------------------------
# Test 7 — Alpha threshold sensitivity
# ---------------------------------------------------------------------------


class TestAlphaThresholdSensitivity:
    """Tighter alpha should make borderline results inconclusive."""

    # Groups with moderate separation → significant at alpha=0.05
    _CTRL_MOD = [10.0, 11.0, 9.0, 10.5, 9.5, 10.2, 9.8, 10.3]
    _TRT_MOD = [11.5, 12.5, 10.5, 12.0, 11.0, 11.8, 10.8, 12.2]

    def test_significant_at_default_alpha(self):
        result = run_ab_test(self._CTRL_MOD, self._TRT_MOD, alpha=0.05)
        assert result.significant is True, "Result must not be empty"

    def test_inconclusive_at_very_tight_alpha(self):
        result = run_ab_test(self._CTRL_MOD, self._TRT_MOD, alpha=0.0001)
        assert result.significant is False, "Result must not be empty"
        assert result.winner == "inconclusive", "Result must not be empty"


# ---------------------------------------------------------------------------
# Test 8 — Treatment winner
# ---------------------------------------------------------------------------


class TestTreatmentWinner:
    def test_treatment_wins_when_treatment_mean_higher(self):
        result = run_ab_test(_CTRL_HIGH_DIFF, _TRT_HIGH_DIFF)
        assert result.winner == "treatment", "Result must not be empty"


# ---------------------------------------------------------------------------
# Test 9 — Control winner
# ---------------------------------------------------------------------------


class TestControlWinner:
    def test_control_wins_when_control_mean_higher(self):
        # Flip: treatment < control
        result = run_ab_test(_TRT_HIGH_DIFF, _CTRL_HIGH_DIFF)
        assert result.winner == "control", "Result must not be empty"


# ---------------------------------------------------------------------------
# Test 10 — ABTest dataclass validation
# ---------------------------------------------------------------------------


class TestABTestDataclassValidation:
    def test_invalid_alpha_raises(self):
        with pytest.raises(ValueError, match="alpha must be in"):
            ABTest("bad", [1.0, 2.0], [1.0, 2.0], alpha=1.5)

    def test_zero_alpha_raises(self):
        with pytest.raises(ValueError, match="alpha must be in"):
            ABTest("bad", [1.0, 2.0], [1.0, 2.0], alpha=0.0)

    def test_insufficient_control_observations_raises(self):
        with pytest.raises(ValueError):
            ABTest("bad", [1.0], [1.0, 2.0])

    def test_insufficient_treatment_observations_raises(self):
        with pytest.raises(ValueError):
            ABTest("bad", [1.0, 2.0], [1.0])

    def test_valid_construction_works(self):
        t = ABTest("ok", [1.0, 2.0], [2.0, 3.0], alpha=0.05)
        assert t.name == "ok", "name is not valid"
        assert t.alpha == 0.05, "alpha is not valid"
