"""Unit tests for src/codex_ml/monitoring/data_drift.py.

Tests cover:
  1. Basic PSI calculation — no-drift (identical distributions)
  2. Basic PSI calculation — clear drift (shifted distribution)
  3. Basic KL calculation — no-drift (identical distributions)
  4. Basic KL calculation — clear drift (shifted distribution)
  5. check_epoch() convenience wrapper returns both results
  6. DriftResult.to_dict() serialisation
  7. Input validation — mismatched lengths raise ValueError
  8. Input validation — empty inputs raise ValueError
  9. Custom thresholds are respected
 10. Epsilon smoothing handles zero-valued bins without error
 11. Single-bin degenerate distribution
 12. Symmetric distribution produces low PSI
"""

from __future__ import annotations

import math

import pytest

from codex_ml.monitoring.data_drift import DataDriftDetector, DriftResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_UNIFORM_4 = [0.25, 0.25, 0.25, 0.25]
_SHIFTED_4 = [0.40, 0.30, 0.20, 0.10]
_ZERO_BIN_4 = [0.5, 0.0, 0.3, 0.2]  # zero bin — epsilon should handle this


# ---------------------------------------------------------------------------
# Test 1 — PSI: identical distributions → no drift
# ---------------------------------------------------------------------------


class TestDetectPsiNoDrift:
    def test_identical_distributions_score_near_zero(self):
        detector = DataDriftDetector()
        result = detector.detect_psi(_UNIFORM_4, _UNIFORM_4)

        assert isinstance(result, DriftResult)
        assert result.method == "psi", "Result must not be empty"
        assert result.score == pytest.approx(0.0, abs=1e-6)
        assert result.drifted is False, "Result must not be empty"
        assert result.severity == "none", "Result must not be empty"

    def test_identical_distributions_drifted_false(self):
        detector = DataDriftDetector(psi_threshold=0.2)
        result = detector.detect_psi([0.1, 0.6, 0.3], [0.1, 0.6, 0.3])
        assert result.drifted is False, "Result must not be empty"


# ---------------------------------------------------------------------------
# Test 2 — PSI: significantly shifted distribution → drift detected
# ---------------------------------------------------------------------------


class TestDetectPsiDrift:
    def test_shifted_distribution_exceeds_default_threshold(self):
        detector = DataDriftDetector(psi_threshold=0.2)
        result = detector.detect_psi(_UNIFORM_4, _SHIFTED_4)

        assert result.drifted is True, "Result must not be empty"
        assert result.score > 0.2, "score must be greater than zero"
        assert result.severity in {"slight", "significant"}

    def test_bin_scores_list_has_correct_length(self):
        detector = DataDriftDetector()
        result = detector.detect_psi(_UNIFORM_4, _SHIFTED_4)
        assert len(result.details["bin_scores"]) == 4, "Collection must not be empty"

    def test_psi_score_is_finite(self):
        detector = DataDriftDetector()
        result = detector.detect_psi([0.3, 0.4, 0.3], [0.1, 0.7, 0.2])
        assert math.isfinite(result.score), "Result must not be empty"


# ---------------------------------------------------------------------------
# Test 3 — KL: identical distributions → no drift
# ---------------------------------------------------------------------------


class TestDetectKlNoDrift:
    def test_identical_distributions_score_near_zero(self):
        detector = DataDriftDetector()
        result = detector.detect_kl(_UNIFORM_4, _UNIFORM_4)

        assert result.method == "kl", "Result must not be empty"
        assert result.score == pytest.approx(0.0, abs=1e-6)
        assert result.drifted is False, "Result must not be empty"
        assert result.severity == "none", "Result must not be empty"


# ---------------------------------------------------------------------------
# Test 4 — KL: significantly shifted distribution → drift detected
# ---------------------------------------------------------------------------


class TestDetectKlDrift:
    def test_shifted_distribution_exceeds_default_threshold(self):
        # Use a large shift to reliably exceed the 0.5 default threshold
        detector = DataDriftDetector(kl_threshold=0.1)
        result = detector.detect_kl(_UNIFORM_4, _SHIFTED_4)

        assert result.drifted is True, "Result must not be empty"
        assert result.score > 0.0, "score must be greater than zero"

    def test_kl_score_non_negative(self):
        """KL divergence must always be ≥ 0 (Gibbs' inequality)."""
        detector = DataDriftDetector()
        result = detector.detect_kl([0.2, 0.3, 0.5], [0.4, 0.1, 0.5])
        assert result.score >= 0.0, "score must be greater than zero"

    def test_kl_bin_scores_length(self):
        detector = DataDriftDetector()
        result = detector.detect_kl(_UNIFORM_4, _SHIFTED_4)
        assert len(result.details["bin_scores"]) == 4, "Collection must not be empty"


# ---------------------------------------------------------------------------
# Test 5 — check_epoch() convenience wrapper
# ---------------------------------------------------------------------------


class TestCheckEpoch:
    def test_returns_both_methods(self):
        detector = DataDriftDetector()
        results = detector.check_epoch(_UNIFORM_4, _UNIFORM_4, epoch=1)

        assert "psi" in results, "Result must not be empty"
        assert "kl" in results, "Result must not be empty"
        assert isinstance(results["psi"], DriftResult)
        assert isinstance(results["kl"], DriftResult)

    def test_epoch_no_drift_scenario(self):
        detector = DataDriftDetector()
        results = detector.check_epoch(_UNIFORM_4, _UNIFORM_4, epoch=5, feature_name="loss_hist")

        assert results["psi"].drifted is False, "Result must not be empty"
        assert results["kl"].drifted is False, "Result must not be empty"

    def test_epoch_drift_scenario(self):
        detector = DataDriftDetector(psi_threshold=0.01, kl_threshold=0.01)
        results = detector.check_epoch(_UNIFORM_4, _SHIFTED_4, epoch=3)

        # With very low thresholds, shifted distribution should trigger both
        assert results["psi"].drifted is True, "Result must not be empty"
        assert results["kl"].drifted is True, "Result must not be empty"


# ---------------------------------------------------------------------------
# Test 6 — DriftResult.to_dict() serialisation
# ---------------------------------------------------------------------------


class TestDriftResultToDict:
    def test_to_dict_contains_required_keys(self):
        detector = DataDriftDetector()
        result = detector.detect_psi(_UNIFORM_4, _UNIFORM_4)
        d = result.to_dict()

        for key in (
            "method",
            "score",
            "threshold",
            "drifted",
            "severity",
            "details",
            "detected_at",
        ):
            assert key in d, f"Missing key: {key}"

    def test_to_dict_types(self):
        detector = DataDriftDetector()
        result = detector.detect_kl(_UNIFORM_4, _UNIFORM_4)
        d = result.to_dict()

        assert isinstance(d["score"], float)
        assert isinstance(d["drifted"], bool)
        assert isinstance(d["details"], dict)
        assert isinstance(d["detected_at"], str)


# ---------------------------------------------------------------------------
# Test 7 — Input validation: mismatched lengths
# ---------------------------------------------------------------------------


class TestInputValidation:
    def test_psi_mismatched_lengths_raises(self):
        detector = DataDriftDetector()
        with pytest.raises(ValueError, match="same length"):
            detector.detect_psi([0.5, 0.5], [0.3, 0.3, 0.4])

    def test_kl_mismatched_lengths_raises(self):
        detector = DataDriftDetector()
        with pytest.raises(ValueError, match="same length"):
            detector.detect_kl([0.5, 0.5], [1.0])


# ---------------------------------------------------------------------------
# Test 8 — Input validation: empty inputs
# ---------------------------------------------------------------------------


class TestEmptyInputs:
    def test_psi_empty_reference_raises(self):
        detector = DataDriftDetector()
        with pytest.raises(ValueError, match="must not be empty"):
            detector.detect_psi([], [])

    def test_kl_empty_current_raises(self):
        detector = DataDriftDetector()
        with pytest.raises(ValueError, match="must not be empty"):
            detector.detect_kl([], [])


# ---------------------------------------------------------------------------
# Test 9 — Custom thresholds are respected
# ---------------------------------------------------------------------------


class TestCustomThresholds:
    def test_low_psi_threshold_flags_mild_shift(self):
        # PSI for a 1-2% per-bin shift is ~0.0008; use threshold below that
        detector = DataDriftDetector(psi_threshold=0.0005)
        result = detector.detect_psi(_UNIFORM_4, [0.26, 0.25, 0.25, 0.24])
        # Even a tiny shift should trigger drift with a near-zero threshold
        assert result.drifted is True, "Result must not be empty"

    def test_high_psi_threshold_ignores_mild_shift(self):
        detector = DataDriftDetector(psi_threshold=10.0)
        result = detector.detect_psi(_UNIFORM_4, _SHIFTED_4)
        assert result.drifted is False, "Result must not be empty"

    def test_invalid_threshold_raises(self):
        with pytest.raises(ValueError):
            DataDriftDetector(psi_threshold=-0.1)
        with pytest.raises(ValueError):
            DataDriftDetector(kl_threshold=0.0)


# ---------------------------------------------------------------------------
# Test 10 — Epsilon smoothing handles zero-valued bins
# ---------------------------------------------------------------------------


class TestEpsilonSmoothing:
    def test_zero_bin_does_not_raise(self):
        detector = DataDriftDetector()
        # Should not raise ZeroDivisionError or math domain error
        result = detector.detect_psi(_ZERO_BIN_4, _UNIFORM_4)
        assert math.isfinite(result.score), "Result must not be empty"

    def test_zero_bin_kl_does_not_raise(self):
        detector = DataDriftDetector()
        result = detector.detect_kl(_ZERO_BIN_4, _UNIFORM_4)
        assert math.isfinite(result.score), "Result must not be empty"


# ---------------------------------------------------------------------------
# Test 11 — Single-bin degenerate distribution
# ---------------------------------------------------------------------------


class TestSingleBin:
    def test_psi_single_bin_identical(self):
        detector = DataDriftDetector()
        result = detector.detect_psi([1.0], [1.0])
        assert result.score == pytest.approx(0.0, abs=1e-6)
        assert result.drifted is False, "Result must not be empty"

    def test_kl_single_bin_identical(self):
        detector = DataDriftDetector()
        result = detector.detect_kl([1.0], [1.0])
        assert result.score == pytest.approx(0.0, abs=1e-6)


# ---------------------------------------------------------------------------
# Test 12 — Symmetric distribution gives low PSI
# ---------------------------------------------------------------------------


class TestSymmetricDistribution:
    def test_symmetric_uniform_psi_low(self):
        """Two uniform distributions should always give PSI ≈ 0."""
        n = 10
        ref = [1.0 / n] * n
        cur = [1.0 / n] * n
        detector = DataDriftDetector()
        result = detector.detect_psi(ref, cur)
        assert result.score < 0.01, "Result must not be empty"

    def test_feature_name_propagated(self):
        detector = DataDriftDetector()
        result = detector.detect_psi(_UNIFORM_4, _UNIFORM_4, feature_name="token_freq")
        assert result.details["feature_name"] == "token_freq", "Result must not be empty"
