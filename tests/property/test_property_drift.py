"""Property-based tests for drift detection modules (Gap 41).

Tests core mathematical properties of DataDriftDetector (PSI and KL-divergence)
and ModelDriftDetector (Jensen-Shannon divergence and confidence monitoring).
"""

from __future__ import annotations

import math
import sys

import pytest

hypothesis = pytest.importorskip("hypothesis")

from hypothesis import assume, given, settings
from hypothesis import strategies as st
from hypothesis.strategies import composite

# ---------------------------------------------------------------------------
# Import production modules
# ---------------------------------------------------------------------------

sys.path.insert(0, "src")

from codex_ml.monitoring.data_drift import DataDriftDetector, DriftResult
from codex_ml.monitoring.model_drift import ModelDriftDetector, jensen_shannon_divergence

# ---------------------------------------------------------------------------
# Shared strategies
# ---------------------------------------------------------------------------

_pos_float_element = st.floats(
    min_value=0.01, max_value=100.0, allow_nan=False, allow_infinity=False
)


@composite
def _paired_pos_float_lists(draw) -> tuple[list[float], list[float]]:
    """Draw two positive-float lists of the same length."""
    n = draw(st.integers(min_value=4, max_value=30))
    ref = draw(st.lists(_pos_float_element, min_size=n, max_size=n))
    cur = draw(st.lists(_pos_float_element, min_size=n, max_size=n))
    return ref, cur


_confidence_scores = st.lists(
    st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    min_size=5,
    max_size=100,
)


# ---------------------------------------------------------------------------
# PSI properties
# ---------------------------------------------------------------------------


class TestPSIProperties:
    """Property tests for Population Stability Index (PSI)."""

    @given(
        st.lists(
            st.floats(min_value=0.01, max_value=100.0, allow_nan=False, allow_infinity=False),
            min_size=4,
            max_size=30,
        )
    )
    @settings(max_examples=50)
    def test_psi_identical_distributions_near_zero(self, vals: list[float]) -> None:
        """PSI between identical distributions must be ≈ 0 (bounded by epsilon smoothing)."""
        detector = DataDriftDetector(psi_threshold=0.2)
        result = detector.detect_psi(vals, vals)
        # With identical inputs the PSI formula gives exactly 0 before smoothing;
        # epsilon smoothing makes reference == current so the result stays 0.
        assert result.score >= 0.0
        assert result.score < 1e-6, (
            f"PSI of identical distributions should be ~0, got {result.score}"
        )

    @given(_paired_pos_float_lists())
    @settings(max_examples=50)
    def test_psi_score_non_negative(
        self, pair: tuple[list[float], list[float]]
    ) -> None:
        """PSI score must always be ≥ 0 for any valid positive inputs."""
        ref, cur = pair
        detector = DataDriftDetector(psi_threshold=0.2)
        result = detector.detect_psi(ref, cur)
        assert result.score >= 0.0, f"PSI score must be non-negative, got {result.score}"

    @given(_paired_pos_float_lists())
    @settings(max_examples=50)
    def test_psi_drifted_flag_consistent_with_threshold(
        self, pair: tuple[list[float], list[float]]
    ) -> None:
        """DriftResult.drifted must be True iff score > threshold."""
        ref, cur = pair
        threshold = 0.2
        detector = DataDriftDetector(psi_threshold=threshold)
        result = detector.detect_psi(ref, cur)
        assert result.drifted == (result.score > threshold)

    @given(_paired_pos_float_lists())
    @settings(max_examples=50)
    def test_psi_severity_is_valid_label(
        self, pair: tuple[list[float], list[float]]
    ) -> None:
        """PSI severity must always be one of the documented labels."""
        ref, cur = pair
        detector = DataDriftDetector(psi_threshold=0.2)
        result = detector.detect_psi(ref, cur)
        assert result.severity in {"none", "slight", "significant"}, (
            f"Unexpected PSI severity: {result.severity!r}"
        )

    @given(_paired_pos_float_lists())
    @settings(max_examples=50)
    def test_psi_result_has_correct_method_field(
        self, pair: tuple[list[float], list[float]]
    ) -> None:
        """DriftResult returned by detect_psi must carry method='psi'."""
        ref, cur = pair
        detector = DataDriftDetector()
        result = detector.detect_psi(ref, cur)
        assert result.method == "psi"


# ---------------------------------------------------------------------------
# KL-divergence properties
# ---------------------------------------------------------------------------


class TestKLProperties:
    """Property tests for KL-divergence drift detection."""

    @given(_pos_floats)
    @settings(max_examples=50)
    def test_kl_identical_distributions_near_zero(self, vals: list[float]) -> None:
        """KL-divergence of identical distributions must be ≈ 0."""
        detector = DataDriftDetector(kl_threshold=0.5)
        result = detector.detect_kl(vals, vals)
        assert result.score >= 0.0
        assert result.score < 1e-6, (
            f"KL of identical distributions should be ~0, got {result.score}"
        )

    @given(_pos_floats, _pos_floats)
    @settings(max_examples=50)
    def test_kl_score_non_negative(
        self, ref: list[float], cur: list[float]
    ) -> None:
        """KL score must always be ≥ 0."""
        assume(len(ref) == len(cur))
        detector = DataDriftDetector(kl_threshold=0.5)
        result = detector.detect_kl(ref, cur)
        assert result.score >= 0.0

    @given(_pos_floats, _pos_floats)
    @settings(max_examples=50)
    def test_kl_drifted_flag_consistent_with_threshold(
        self, ref: list[float], cur: list[float]
    ) -> None:
        """KL DriftResult.drifted must match score > threshold."""
        assume(len(ref) == len(cur))
        threshold = 0.5
        detector = DataDriftDetector(kl_threshold=threshold)
        result = detector.detect_kl(ref, cur)
        assert result.drifted == (result.score > threshold), (
            f"drifted={result.drifted} inconsistent with score={result.score} "
            f"vs threshold={threshold}"
        )

    @given(_pos_floats, _pos_floats)
    @settings(max_examples=50)
    def test_kl_result_has_correct_method_field(
        self, ref: list[float], cur: list[float]
    ) -> None:
        """DriftResult returned by detect_kl must carry method='kl'."""
        assume(len(ref) == len(cur))
        detector = DataDriftDetector()
        result = detector.detect_kl(ref, cur)
        assert result.method == "kl"

    @given(_pos_floats, _pos_floats)
    @settings(max_examples=50)
    def test_kl_severity_is_valid_label(
        self, ref: list[float], cur: list[float]
    ) -> None:
        """KL severity must always be one of the documented labels."""
        assume(len(ref) == len(cur))
        detector = DataDriftDetector(kl_threshold=0.5)
        result = detector.detect_kl(ref, cur)
        assert result.severity in {"none", "moderate", "significant"}, (
            f"Unexpected KL severity: {result.severity!r}"
        )


# ---------------------------------------------------------------------------
# Threshold monotonicity property
# ---------------------------------------------------------------------------


class TestThresholdMonotonicity:
    """Higher drift → more likely to be flagged (threshold monotonicity)."""

    @given(_pos_floats)
    @settings(max_examples=50)
    def test_lower_threshold_flags_at_least_as_often_as_higher_threshold(
        self, vals: list[float]
    ) -> None:
        """A detector with a lower threshold flags at least as often as one with a higher threshold."""
        # Use a fixed "drifted" distribution: scale by 10x to induce drift
        cur = [v * 10.0 for v in vals]

        strict_detector = DataDriftDetector(psi_threshold=0.01, kl_threshold=0.01)
        loose_detector = DataDriftDetector(psi_threshold=10.0, kl_threshold=10.0)

        strict_result = strict_detector.detect_psi(vals, cur)
        loose_result = loose_detector.detect_psi(vals, cur)

        # If the loose detector flags drift, so must the strict one
        # (the score is the same; only the threshold differs)
        if loose_result.drifted:
            assert strict_result.drifted, (
                "Strict detector should flag drift whenever loose detector does"
            )


# ---------------------------------------------------------------------------
# JSD properties (ModelDriftDetector helper)
# ---------------------------------------------------------------------------


class TestJSDProperties:
    """Property tests for jensen_shannon_divergence."""

    @given(
        st.lists(
            st.floats(min_value=0.01, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=2,
            max_size=20,
        )
    )
    @settings(max_examples=50)
    def test_jsd_identical_distributions_is_zero(self, vals: list[float]) -> None:
        """JSD of identical distributions must be 0."""
        result = jensen_shannon_divergence(vals, vals)
        assert math.isclose(result, 0.0, abs_tol=1e-9), (
            f"JSD(P, P) should be 0, got {result}"
        )

    @given(
        st.lists(
            st.floats(min_value=0.01, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=2,
            max_size=20,
        ),
        st.lists(
            st.floats(min_value=0.01, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=2,
            max_size=20,
        ),
    )
    @settings(max_examples=50)
    def test_jsd_result_in_unit_interval(
        self, p: list[float], q: list[float]
    ) -> None:
        """JSD must always be in [0, 1]."""
        assume(len(p) == len(q))
        result = jensen_shannon_divergence(p, q)
        assert 0.0 <= result <= 1.0, f"JSD must be in [0, 1], got {result}"
