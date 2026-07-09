"""A/B testing framework for Codex ML experiments.

Provides statistical hypothesis testing (Welch's t-test) with:
- Cohen's d effect size
- Confidence interval estimation
- Multi-test suite management

Uses scipy.stats when available; falls back to a pure-stdlib
Welch/t-distribution approximation (Welch-Satterthwaite degrees of freedom)
so the module is importable in environments without scipy.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

# ---------------------------------------------------------------------------
# Optional scipy import
# ---------------------------------------------------------------------------
try:
    from scipy import stats as _scipy_stats

    _SCIPY_AVAILABLE = True
except ModuleNotFoundError:
    _SCIPY_AVAILABLE = False


# ---------------------------------------------------------------------------
# Pure-stdlib helpers (used when scipy is absent)
# ---------------------------------------------------------------------------


def _mean(data: Sequence[float]) -> float:
    n = len(data)
    if n == 0:
        raise ValueError("Cannot compute mean of empty sequence.")
    return sum(data) / n


def _variance(data: Sequence[float]) -> float:
    """Sample variance (Bessel-corrected, ddof=1)."""
    n = len(data)
    if n < 2:
        raise ValueError("Variance requires at least 2 data points.")
    mu = _mean(data)
    return sum((x - mu) ** 2 for x in data) / (n - 1)


def _welch_t_stat(
    mean1: float,
    var1: float,
    n1: int,
    mean2: float,
    var2: float,
    n2: int,
) -> float:
    """Welch's t-statistic."""
    denom = math.sqrt(var1 / n1 + var2 / n2)
    if denom == 0.0:
        return 0.0
    return (mean1 - mean2) / denom


def _welch_df(var1: float, n1: int, var2: float, n2: int) -> float:
    """Welch-Satterthwaite degrees of freedom."""
    a = var1 / n1
    b = var2 / n2
    numerator = (a + b) ** 2
    denominator = (a**2) / (n1 - 1) + (b**2) / (n2 - 1)
    if denominator == 0.0:
        return float(n1 + n2 - 2)
    return numerator / denominator


def _regularized_incomplete_beta(a: float, b: float, x: float) -> float:
    """Incomplete beta function I_x(a, b) via continued-fraction expansion.

    Used to compute the CDF of the t-distribution.
    """
    if x < 0.0 or x > 1.0:
        raise ValueError(f"x={x} out of [0, 1]")
    if x == 0.0:
        return 0.0
    if x == 1.0:
        return 1.0

    # Use the symmetry relation when x > (a+1)/(a+b+2) for convergence
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - _regularized_incomplete_beta(b, a, 1.0 - x)

    lbeta_ab = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(math.log(x) * a + math.log(1.0 - x) * b - lbeta_ab) / a

    # Lentz's continued fraction
    tiny = 1e-300
    fprev = tiny
    C = fprev
    D = 0.0
    for m in range(200):
        for step in range(2):
            if step == 0:
                if m == 0:
                    d = 1.0
                else:
                    d = m * (b - m) * x / ((a + 2.0 * m - 1.0) * (a + 2.0 * m))
            else:
                d = -(a + m) * (a + b + m) * x / ((a + 2.0 * m) * (a + 2.0 * m + 1.0))
            D = 1.0 + d * D
            if abs(D) < tiny:
                D = tiny
            C = 1.0 + d / C
            if abs(C) < tiny:
                C = tiny
            D = 1.0 / D
            delta = C * D
            fprev *= delta
            if abs(delta - 1.0) < 1e-10:
                return front * fprev
    return front * fprev


def _t_cdf(t: float, df: float) -> float:
    """CDF of the t-distribution at *t* with *df* degrees of freedom."""
    x = df / (df + t * t)
    ib = _regularized_incomplete_beta(df / 2.0, 0.5, x)
    p = ib / 2.0
    if t >= 0:
        return 1.0 - p
    return p


def _two_tailed_p(t_stat: float, df: float) -> float:
    """Two-tailed p-value for Welch's t-test."""
    return 2.0 * min(_t_cdf(abs(t_stat), df), 1.0 - _t_cdf(abs(t_stat), df))


def _t_critical(alpha: float, df: float) -> float:
    """Two-tailed critical t-value for significance level *alpha*.

    Solved by binary search on the t-CDF.
    """
    target = 1.0 - alpha / 2.0
    lo, hi = 0.0, 1e6
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if _t_cdf(mid, df) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _stdlib_ttest_ind(
    a: Sequence[float],
    b: Sequence[float],
) -> tuple[float, float]:
    """Pure-stdlib Welch's t-test.  Returns (t_statistic, p_value)."""
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        raise ValueError("Each group needs at least 2 observations.")
    m1, m2 = _mean(a), _mean(b)
    v1, v2 = _variance(a), _variance(b)
    t_stat = _welch_t_stat(m1, v1, n1, m2, v2, n2)
    df = _welch_df(v1, n1, v2, n2)
    p_val = _two_tailed_p(t_stat, df)
    return t_stat, p_val


# ---------------------------------------------------------------------------
# Public dataclasses
# ---------------------------------------------------------------------------


@dataclass
class ABTest:
    """Container for a single A/B test configuration and raw metrics."""

    name: str
    control_metrics: list[float]
    treatment_metrics: list[float]
    alpha: float = 0.05

    def __post_init__(self) -> None:
        if not 0.0 < self.alpha < 1.0:
            raise ValueError(f"alpha must be in (0, 1), got {self.alpha!r}")
        if len(self.control_metrics) < 2 or len(self.treatment_metrics) < 2:
            raise ValueError("Each group needs at least 2 observations.")


@dataclass
class ABTestResult:
    """Structured result of a single A/B test."""

    winner: str  # "control" | "treatment" | "inconclusive"
    p_value: float
    effect_size: float  # Cohen's d
    confidence_interval: tuple[float, float]  # 95 % CI of the mean difference
    significant: bool

    def __post_init__(self) -> None:
        valid = {"control", "treatment", "inconclusive"}
        if self.winner not in valid:
            raise ValueError(f"winner must be one of {valid}, got {self.winner!r}")


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------


def run_ab_test(
    control_metrics: Sequence[float],
    treatment_metrics: Sequence[float],
    metric_name: str = "metric",
    alpha: float = 0.05,
) -> ABTestResult:
    """Run a Welch's t-test comparing *control_metrics* vs *treatment_metrics*.

    Parameters
    ----------
    control_metrics:
        Observed values for the control group.
    treatment_metrics:
        Observed values for the treatment group.
    metric_name:
        Human-readable label (used for error messages only).
    alpha:
        Significance level, default ``0.05``.

    Returns
    -------
    ABTestResult
        Structured result including winner, p-value, Cohen's d, and the
        confidence interval of the mean difference.
    """
    ctrl = list(control_metrics)
    trt = list(treatment_metrics)

    if len(ctrl) < 2:
        raise ValueError(f"{metric_name}: control group needs ≥2 observations, got {len(ctrl)}")
    if len(trt) < 2:
        raise ValueError(f"{metric_name}: treatment group needs ≥2 observations, got {len(trt)}")

    n1, n2 = len(ctrl), len(trt)
    mean_ctrl = _mean(ctrl)
    mean_trt = _mean(trt)
    var_ctrl = _variance(ctrl)
    var_trt = _variance(trt)

    # --- t-test ---
    if _SCIPY_AVAILABLE:
        _, p_value = _scipy_stats.ttest_ind(ctrl, trt, equal_var=False)
        p_value = float(p_value)
    else:
        _, p_value = _stdlib_ttest_ind(ctrl, trt)

    # --- Cohen's d (pooled std, Welch variant) ---
    pooled_std = math.sqrt((var_ctrl * (n1 - 1) + var_trt * (n2 - 1)) / (n1 + n2 - 2))
    effect_size = (mean_trt - mean_ctrl) / pooled_std if pooled_std != 0.0 else 0.0

    # --- Confidence interval of the mean difference (treatment − control) ---
    df = _welch_df(var_ctrl, n1, var_trt, n2)
    se_diff = math.sqrt(var_ctrl / n1 + var_trt / n2)
    if _SCIPY_AVAILABLE:
        t_crit = float(_scipy_stats.t.ppf(1.0 - alpha / 2.0, df))
    else:
        t_crit = _t_critical(alpha, df)
    mean_diff = mean_trt - mean_ctrl
    ci_lower = mean_diff - t_crit * se_diff
    ci_upper = mean_diff + t_crit * se_diff

    # --- Significance & winner ---
    significant = p_value < alpha
    if not significant:
        winner = "inconclusive"
    elif mean_trt > mean_ctrl:
        winner = "treatment"
    else:
        winner = "control"

    return ABTestResult(
        winner=winner,
        p_value=p_value,
        effect_size=effect_size,
        confidence_interval=(ci_lower, ci_upper),
        significant=significant,
    )


# ---------------------------------------------------------------------------
# Suite
# ---------------------------------------------------------------------------


class ABTestSuite:
    """Manage and run multiple :class:`ABTest` instances.

    Example
    -------
    >>> suite = ABTestSuite()
    >>> suite.add_test(ABTest("revenue", ctrl, trt))
    >>> results = suite.run_all()
    >>> report = suite.report()
    """

    def __init__(self) -> None:
        self._tests: dict[str, ABTest] = {}
        self._results: dict[str, ABTestResult] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_test(self, test: ABTest) -> None:
        """Register an :class:`ABTest`.  Overwrites any previous test with
        the same name."""
        if not isinstance(test, ABTest):
            raise TypeError(f"Expected ABTest, got {type(test).__name__}")
        self._tests[test.name] = test

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run_all(self) -> dict[str, ABTestResult]:
        """Execute all registered tests and cache the results.

        Returns
        -------
        dict[str, ABTestResult]
            Mapping of test name → result.
        """
        self._results = {}
        for name, test in self._tests.items():
            self._results[name] = run_ab_test(
                control_metrics=test.control_metrics,
                treatment_metrics=test.treatment_metrics,
                metric_name=name,
                alpha=test.alpha,
            )
        return dict(self._results)

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def report(self) -> dict[str, Any]:
        """Build a structured summary report.

        Calls :meth:`run_all` if results are not yet available.

        Returns
        -------
        dict
            ``{
              "summary": {"total": N, "significant": K, "inconclusive": M},
              "tests": {<name>: {...}, ...}
            }``
        """
        if not self._results:
            self.run_all()

        tests_report: dict[str, Any] = {}
        significant_count = 0
        inconclusive_count = 0

        for name, result in self._results.items():
            tests_report[name] = {
                "winner": result.winner,
                "p_value": result.p_value,
                "effect_size": result.effect_size,
                "confidence_interval": list(result.confidence_interval),
                "significant": result.significant,
            }
            if result.significant:
                significant_count += 1
            else:
                inconclusive_count += 1

        return {
            "summary": {
                "total": len(self._results),
                "significant": significant_count,
                "inconclusive": inconclusive_count,
            },
            "tests": tests_report,
        }
