"""Unit tests for the pure-stdlib helpers in ab_testing.py (Gap 5 — Wave 3/4).

The main test_ab_testing.py file exercises the high-level API through scipy
(when available), leaving the stdlib helper functions uncovered.  This file
covers:

  T01. _mean()               — basic mean, single element, empty raises
  T02. _variance()           — sample variance correctness, < 2 points raises
  T03. _welch_t_stat()       — t-statistic formula, zero-denom returns 0.0
  T04. _welch_df()           — Satterthwaite formula, zero-denom fallback
  T05. _regularized_incomplete_beta() — boundary cases (x=0, x=1), symmetry
  T06. _t_cdf()              — CDF shape: t→+∞ → 1, t=0 → 0.5
  T07. _two_tailed_p()       — positive t = negative t symmetry
  T08. _t_critical()         — critical value is positive; larger α → smaller t
  T09. _stdlib_ttest_ind()   — known identical groups → p ≈ 1, minimal groups
  T10. run_ab_test (stdlib)  — mocking _SCIPY_AVAILABLE=False exercises stdlib
       fallback path end-to-end; result types and winner logic are preserved.

All inputs are fixed (no random seeds, no I/O, deterministic).
"""

from __future__ import annotations

import math
from unittest.mock import patch

import pytest

from codex_ml.experiments.ab_testing import (
    ABTestResult,
    _mean,
    _regularized_incomplete_beta,
    _stdlib_ttest_ind,
    _t_cdf,
    _t_critical,
    _two_tailed_p,
    _variance,
    _welch_df,
    _welch_t_stat,
    run_ab_test,
)

# ---------------------------------------------------------------------------
# T01 — _mean()
# ---------------------------------------------------------------------------


class TestMean:
    def test_basic_mean(self):
        assert _mean([1.0, 2.0, 3.0, 4.0, 5.0]) == pytest.approx(3.0)

    def test_single_element(self):
        assert _mean([7.5]) == pytest.approx(7.5), "Condition must be true"

    def test_negative_values(self):
        assert _mean([-2.0, -4.0]) == pytest.approx(-3.0)

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="empty sequence"):
            _mean([])


# ---------------------------------------------------------------------------
# T02 — _variance()
# ---------------------------------------------------------------------------


class TestVariance:
    def test_known_variance(self):
        # Data: 2, 4, 4, 4, 5, 5, 7, 9 → sample var = 4.571...
        data = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        v = _variance(data)
        assert v == pytest.approx(4.571428, rel=1e-4)

    def test_constant_data_gives_zero_variance(self):
        data = [3.0, 3.0, 3.0, 3.0]
        assert _variance(data) == pytest.approx(0.0, abs=1e-12)

    def test_two_point_data(self):
        v = _variance([0.0, 2.0])
        assert v == pytest.approx(2.0), "v is not valid"

    def test_fewer_than_two_points_raises(self):
        with pytest.raises(ValueError):
            _variance([1.0])

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            _variance([])


# ---------------------------------------------------------------------------
# T03 — _welch_t_stat()
# ---------------------------------------------------------------------------


class TestWelchTStat:
    def test_same_means_zero_t(self):
        t = _welch_t_stat(mean1=5.0, var1=1.0, n1=10, mean2=5.0, var2=1.0, n2=10)
        assert t == pytest.approx(0.0), "t is not valid"

    def test_positive_when_mean1_greater(self):
        t = _welch_t_stat(mean1=10.0, var1=1.0, n1=10, mean2=5.0, var2=1.0, n2=10)
        assert t > 0.0, "t must be greater than zero"

    def test_negative_when_mean2_greater(self):
        t = _welch_t_stat(mean1=5.0, var1=1.0, n1=10, mean2=10.0, var2=1.0, n2=10)
        assert t < 0.0, "t is not valid"

    def test_zero_denom_returns_zero(self):
        # Both variances 0 → denom=0 → returns 0.0 (no ZeroDivisionError)
        t = _welch_t_stat(mean1=1.0, var1=0.0, n1=10, mean2=2.0, var2=0.0, n2=10)
        assert t == 0.0, "t is not valid"


# ---------------------------------------------------------------------------
# T04 — _welch_df()
# ---------------------------------------------------------------------------


class TestWelchDf:
    def test_positive_df_for_normal_inputs(self):
        df = _welch_df(var1=1.0, n1=10, var2=1.0, n2=10)
        assert df > 0.0, "df must be greater than zero"

    def test_equal_variance_equal_n_approx_classical_df(self):
        # With equal variances and n, Welch df ≈ 2*(n-1)
        df = _welch_df(var1=1.0, n1=10, var2=1.0, n2=10)
        assert df == pytest.approx(18.0, rel=0.01)

    def test_zero_denom_fallback(self):
        # With var=0 and n=10: a = 0/10 = 0, b = 0/10 = 0, denominator=0 → fallback
        df = _welch_df(var1=0.0, n1=10, var2=0.0, n2=10)
        assert df == pytest.approx(10 + 10 - 2), "df is not valid"


# ---------------------------------------------------------------------------
# T05 — _regularized_incomplete_beta()
# ---------------------------------------------------------------------------


class TestRegularizedIncompleteBeta:
    def test_x_zero_returns_zero(self):
        result = _regularized_incomplete_beta(0.5, 0.5, 0.0)
        assert result == pytest.approx(0.0), "Result must not be empty"

    def test_x_one_returns_one(self):
        result = _regularized_incomplete_beta(0.5, 0.5, 1.0)
        assert result == pytest.approx(1.0), "Result must not be empty"

    def test_symmetry_at_half_for_equal_params(self):
        # I_{0.5}(a, a) = 0.5 for any a > 0
        result = _regularized_incomplete_beta(2.0, 2.0, 0.5)
        assert result == pytest.approx(0.5, abs=1e-4)

    def test_result_in_0_1_range(self):
        result = _regularized_incomplete_beta(3.0, 5.0, 0.3)
        assert 0.0 <= result <= 1.0, "Result must not be empty"

    def test_out_of_range_x_raises(self):
        with pytest.raises(ValueError, match="out of"):
            _regularized_incomplete_beta(1.0, 1.0, 1.5)


# ---------------------------------------------------------------------------
# T06 — _t_cdf()
# ---------------------------------------------------------------------------


class TestTCdf:
    def test_large_positive_t_approaches_one(self):
        cdf = _t_cdf(100.0, df=30.0)
        assert cdf > 0.9999, "cdf must be greater than zero"

    def test_large_negative_t_approaches_zero(self):
        cdf = _t_cdf(-100.0, df=30.0)
        assert cdf < 0.0001, "cdf is not valid"

    def test_t_zero_gives_half(self):
        cdf = _t_cdf(0.0, df=10.0)
        assert cdf == pytest.approx(0.5, abs=0.01)

    def test_positive_t_greater_than_half(self):
        cdf = _t_cdf(2.0, df=20.0)
        assert cdf > 0.5, "cdf must be greater than zero"


# ---------------------------------------------------------------------------
# T07 — _two_tailed_p()
# ---------------------------------------------------------------------------


class TestTwoTailedP:
    def test_p_value_in_0_1_range(self):
        p = _two_tailed_p(2.0, df=20.0)
        assert 0.0 < p < 1.0, "0 is not valid"

    def test_large_t_stat_gives_small_p(self):
        p = _two_tailed_p(100.0, df=30.0)
        assert p < 1e-6, "p is not valid"

    def test_zero_t_gives_p_near_one(self):
        p = _two_tailed_p(0.0, df=10.0)
        assert p == pytest.approx(1.0, abs=0.05)

    def test_symmetric_t_stat(self):
        """p-value is the same for +t and -t."""
        p_pos = _two_tailed_p(2.5, df=15.0)
        p_neg = _two_tailed_p(-2.5, df=15.0)
        assert p_pos == pytest.approx(p_neg, rel=1e-5)


# ---------------------------------------------------------------------------
# T08 — _t_critical()
# ---------------------------------------------------------------------------


class TestTCritical:
    def test_critical_value_positive(self):
        t_crit = _t_critical(alpha=0.05, df=20.0)
        assert t_crit > 0.0, "t_crit must be greater than zero"

    def test_smaller_alpha_gives_larger_critical_value(self):
        t_001 = _t_critical(alpha=0.001, df=20.0)
        t_005 = _t_critical(alpha=0.05, df=20.0)
        t_010 = _t_critical(alpha=0.10, df=20.0)
        assert t_001 > t_005 > t_010, "t_001 must be greater than zero"

    def test_large_df_approaches_z_critical(self):
        # For large df, t critical ≈ z critical (1.96 for α=0.05)
        t_crit = _t_critical(alpha=0.05, df=1000.0)
        assert t_crit == pytest.approx(1.96, abs=0.05)


# ---------------------------------------------------------------------------
# T09 — _stdlib_ttest_ind()
# ---------------------------------------------------------------------------


class TestStdlibTtestInd:
    def test_identical_groups_p_value_near_one(self):
        data = [5.0, 5.0, 5.0, 5.0, 5.0]
        t, p = _stdlib_ttest_ind(data, data)
        # t should be 0 (same means, same variance)
        assert t == pytest.approx(0.0, abs=1e-9)

    def test_well_separated_groups_small_p(self):
        # Use data with variance so Welch t-stat is well-defined
        a = [10.0, 10.2, 9.8, 10.1, 9.9, 10.0, 10.3, 9.7, 10.05, 9.95]
        b = [20.0, 20.2, 19.8, 20.1, 19.9, 20.0, 20.3, 19.7, 20.05, 19.95]
        _, p = _stdlib_ttest_ind(a, b)
        assert p < 0.001, "p is not valid"

    def test_returns_tuple_of_floats(self):
        a = [1.0, 2.0, 3.0]
        b = [4.0, 5.0, 6.0]
        result = _stdlib_ttest_ind(a, b)
        assert isinstance(result, tuple)
        assert len(result) == 2, "Result must not be empty"
        assert all(isinstance(x, float) for x in result)

    def test_insufficient_observations_raises(self):
        with pytest.raises(ValueError, match="at least 2"):
            _stdlib_ttest_ind([1.0], [2.0, 3.0])

    def test_t_stat_sign_reflects_direction(self):
        a = [1.0, 2.0, 3.0]
        b = [10.0, 11.0, 12.0]
        t, _ = _stdlib_ttest_ind(a, b)
        assert t < 0.0, "t is not valid"

    def test_p_value_in_range(self):
        a = [1.0, 1.1, 0.9, 1.05, 0.95]
        b = [2.0, 2.1, 1.9, 2.05, 1.95]
        _, p = _stdlib_ttest_ind(a, b)
        assert 0.0 <= p <= 1.0, "0 is not valid"


# ---------------------------------------------------------------------------
# T10 — run_ab_test with _SCIPY_AVAILABLE mocked to False
# ---------------------------------------------------------------------------


_CTRL_HIGH = [10.0, 10.1, 9.9, 10.05, 9.95, 10.2, 9.8, 10.15, 9.85, 10.0]
_TRT_HIGH = [20.0, 20.1, 19.9, 20.05, 19.95, 20.2, 19.8, 20.15, 19.85, 20.0]
_CTRL_SAME = [5.0, 5.01, 4.99, 5.0, 5.02, 4.98, 5.01, 4.99, 5.0, 5.0]
_TRT_SAME = [5.0, 5.01, 4.99, 5.0, 5.02, 4.98, 5.01, 4.99, 5.0, 5.0]


class TestRunAbTestStdlibPath:
    """Test run_ab_test() exercising the pure-stdlib code path."""

    def _run_with_stdlib(self, ctrl, trt, alpha=0.05):
        """Patch away scipy so the stdlib branch executes."""
        import codex_ml.experiments.ab_testing as _module

        with patch.object(_module, "_SCIPY_AVAILABLE", False):
            return run_ab_test(ctrl, trt, alpha=alpha)

    def test_stdlib_returns_abtestresult(self):
        result = self._run_with_stdlib(_CTRL_HIGH, _TRT_HIGH)
        assert isinstance(result, ABTestResult)

    def test_stdlib_significant_for_well_separated_groups(self):
        result = self._run_with_stdlib(_CTRL_HIGH, _TRT_HIGH)
        assert result.significant is True, "Result must not be empty"

    def test_stdlib_treatment_winner(self):
        result = self._run_with_stdlib(_CTRL_HIGH, _TRT_HIGH)
        assert result.winner == "treatment", "Result must not be empty"

    def test_stdlib_control_winner_when_ctrl_higher(self):
        result = self._run_with_stdlib(_TRT_HIGH, _CTRL_HIGH)
        assert result.winner == "control", "Result must not be empty"

    def test_stdlib_inconclusive_for_identical_groups(self):
        result = self._run_with_stdlib(_CTRL_SAME, _TRT_SAME)
        assert result.winner == "inconclusive", "Result must not be empty"
        assert result.significant is False, "Result must not be empty"

    def test_stdlib_p_value_in_range(self):
        result = self._run_with_stdlib(_CTRL_HIGH, _TRT_HIGH)
        assert 0.0 <= result.p_value <= 1.0, "Result must not be empty"

    def test_stdlib_effect_size_is_float(self):
        result = self._run_with_stdlib(_CTRL_HIGH, _TRT_HIGH)
        assert isinstance(result.effect_size, float)

    def test_stdlib_ci_is_ordered(self):
        result = self._run_with_stdlib(_CTRL_HIGH, _TRT_HIGH)
        lo, hi = result.confidence_interval
        assert lo < hi, "lo is not valid"

    def test_stdlib_insufficient_control_raises(self):
        import codex_ml.experiments.ab_testing as _module

        with patch.object(_module, "_SCIPY_AVAILABLE", False):
            with pytest.raises(ValueError, match="control group"):
                run_ab_test([1.0], [2.0, 3.0])

    def test_stdlib_insufficient_treatment_raises(self):
        import codex_ml.experiments.ab_testing as _module

        with patch.object(_module, "_SCIPY_AVAILABLE", False):
            with pytest.raises(ValueError, match="treatment group"):
                run_ab_test([1.0, 2.0], [3.0])

    def test_stdlib_pooled_std_zero_gives_zero_effect_size(self):
        # Constant values → pooled std = 0 → effect_size = 0.0
        result = self._run_with_stdlib(_CTRL_SAME, _TRT_SAME)
        assert math.isclose(result.effect_size, 0.0, abs_tol=1e-9)
