"""Unit tests for src/codex_ml/monitoring/model_drift.py (Gap 18).

Tests cover:
- T01: JSD helper (identical distributions → 0, maximally different → 1)
- T02: JSD detects output distribution shift
- T03: Confidence-drop detection
- T04: Low-confidence-rate detection
- T05: No-drift on stable data
- T06: Baseline management (has_baseline / update_baseline / reset)
- T07: DriftResult.summary() and to_dict() shape
- T08: ConfidenceStats.from_scores() statistics
- T09: First epoch auto-sets baseline; second epoch triggers drift
- T10: ModelDriftDetector raises ValueError on bad inputs
"""

from __future__ import annotations

import pytest

from codex_ml.monitoring.model_drift import (
    ConfidenceStats,
    DriftResult,
    ModelDriftDetector,
    jensen_shannon_divergence,
)

# ---------------------------------------------------------------------------
# T01 — JSD helper: edge-case values
# ---------------------------------------------------------------------------


class TestJensenShannonDivergence:
    """T01: Basic JSD correctness."""

    def test_identical_distributions_give_zero(self):
        """JSD(P, P) must be 0."""
        p = [0.25, 0.25, 0.25, 0.25]
        assert jensen_shannon_divergence(p, p) == pytest.approx(0.0, abs=1e-9)

    def test_uniform_vs_uniform_is_zero(self):
        n = 8
        p = [1.0 / n] * n
        q = [1.0 / n] * n
        assert jensen_shannon_divergence(p, q) == pytest.approx(0.0, abs=1e-9)

    def test_maximally_different_distributions(self):
        """JSD between disjoint distributions should equal 1.0."""
        p = [1.0, 0.0]
        q = [0.0, 1.0]
        assert jensen_shannon_divergence(p, q) == pytest.approx(1.0, abs=1e-9)

    def test_result_bounded_zero_one(self):
        """JSD must always lie in [0, 1]."""
        import random

        rng = random.Random(42)
        for _ in range(20):
            n = rng.randint(2, 10)
            raw_p = [rng.random() + 0.001 for _ in range(n)]
            raw_q = [rng.random() + 0.001 for _ in range(n)]
            jsd = jensen_shannon_divergence(raw_p, raw_q)
            assert 0.0 <= jsd <= 1.0 + 1e-9, "0 is not valid"

    def test_mismatched_lengths_raises(self):
        with pytest.raises(ValueError, match="same length"):
            jensen_shannon_divergence([0.5, 0.5], [0.3, 0.3, 0.4])

    def test_empty_input_raises(self):
        with pytest.raises(ValueError):
            jensen_shannon_divergence([], [])


# ---------------------------------------------------------------------------
# T02 — JSD detects output distribution shift
# ---------------------------------------------------------------------------


class TestJSDDriftDetection:
    """T02: ModelDriftDetector detects output-distribution shift via JSD."""

    def test_large_distribution_shift_triggers_drift(self):
        """High-confidence baseline vs low-confidence current → drift."""
        detector = ModelDriftDetector(js_threshold=0.05, confidence_threshold=0.0)
        baseline = [0.95] * 50  # all high-confidence
        detector.update_baseline(baseline)

        current = [0.05] * 50  # all low-confidence
        result = detector.check(current, epoch=1)

        assert result.drift_detected is True, "Result must not be empty"
        assert result.js_divergence is not None, "js_divergence must be initialized"
        assert result.js_divergence > 0.05, "js_divergence must be greater than zero"
        assert any("JSD" in r for r in result.reasons), "Result must not be empty"

    def test_similar_distributions_no_jsd_drift(self):
        """Near-identical distributions should not trigger JSD drift."""
        detector = ModelDriftDetector(
            js_threshold=0.1, confidence_threshold=0.0, low_confidence_rate_threshold=1.0
        )
        baseline = [0.8 + 0.01 * (i % 5) for i in range(50)]
        detector.update_baseline(baseline)

        current = [0.8 + 0.01 * (i % 5) for i in range(50)]
        result = detector.check(current, epoch=1)

        assert result.js_divergence is not None, "js_divergence must be initialized"
        assert result.js_divergence < 0.1, "Result must not be empty"
        # JSD alone should not trigger drift
        jsd_triggered = any("JSD" in r for r in result.reasons)
        assert not jsd_triggered, "Condition must be true"


# ---------------------------------------------------------------------------
# T03 — Confidence-drop detection
# ---------------------------------------------------------------------------


class TestConfidenceDropDetection:
    """T03: Confidence-drop alert when mean confidence falls below threshold."""

    def test_low_mean_confidence_triggers_alert(self):
        detector = ModelDriftDetector(
            js_threshold=1.0,  # disable JSD gate
            confidence_threshold=0.6,
            low_confidence_rate_threshold=1.0,  # disable low-rate gate
        )
        scores = [0.2, 0.3, 0.25, 0.35, 0.28]
        result = detector.check(scores, epoch=3)

        assert result.drift_detected is True, "Result must not be empty"
        assert result.confidence_dropped is True, "Result must not be empty"
        assert result.confidence_stats is not None, "confidence_stats must be initialized"
        assert result.confidence_stats.mean_confidence < 0.6, "Result must not be empty"

    def test_high_mean_confidence_no_alert(self):
        detector = ModelDriftDetector(
            js_threshold=1.0,
            confidence_threshold=0.5,
            low_confidence_rate_threshold=1.0,
        )
        scores = [0.9, 0.85, 0.92, 0.88, 0.91]
        result = detector.check(scores, epoch=1)

        assert result.confidence_dropped is False, "Result must not be empty"
        assert not any("mean_confidence" in r for r in result.reasons), "Result must not be empty"


# ---------------------------------------------------------------------------
# T04 — Low-confidence-rate detection
# ---------------------------------------------------------------------------


class TestLowConfidenceRateDetection:
    """T04: Drift triggered when too many predictions are low-confidence."""

    def test_high_low_confidence_rate_triggers_drift(self):
        detector = ModelDriftDetector(
            js_threshold=1.0,
            confidence_threshold=0.0,  # disable mean gate
            low_confidence_rate_threshold=0.3,
            low_conf_score_cutoff=0.5,
        )
        # 80% of scores are below 0.5
        scores = [0.2] * 40 + [0.8] * 10
        result = detector.check(scores, epoch=2)

        assert result.drift_detected is True, "Result must not be empty"
        assert result.confidence_stats.low_confidence_rate > 0.3, "low_confidence_rate must be greater than zero"
        assert any("low_confidence_rate" in r for r in result.reasons), "Result must not be empty"

    def test_low_low_confidence_rate_no_drift(self):
        detector = ModelDriftDetector(
            js_threshold=1.0,
            confidence_threshold=0.0,
            low_confidence_rate_threshold=0.3,
            low_conf_score_cutoff=0.5,
        )
        # Only 10% below threshold
        scores = [0.2] * 5 + [0.8] * 45
        result = detector.check(scores, epoch=2)

        low_rate_triggered = any("low_confidence_rate" in r for r in result.reasons)
        assert not low_rate_triggered, "Condition must be true"


# ---------------------------------------------------------------------------
# T05 — No drift on stable data
# ---------------------------------------------------------------------------


class TestNoDriftStableData:
    """T05: Stable, high-confidence scores produce no drift signal."""

    def test_stable_high_confidence_no_drift(self):
        detector = ModelDriftDetector(
            js_threshold=0.05,
            confidence_threshold=0.5,
            low_confidence_rate_threshold=0.3,
        )
        stable_scores = [0.85, 0.90, 0.88, 0.87, 0.92] * 10
        detector.update_baseline(stable_scores)

        result = detector.check(stable_scores, epoch=5)

        assert result.drift_detected is False, "Result must not be empty"
        assert result.reasons == [], "Result must not be empty"
        assert "No drift" in result.summary(), "Result must not be empty"


# ---------------------------------------------------------------------------
# T06 — Baseline management
# ---------------------------------------------------------------------------


class TestBaselineManagement:
    """T06: has_baseline / update_baseline / reset."""

    def test_no_baseline_initially(self):
        detector = ModelDriftDetector()
        assert detector.has_baseline() is False, "detect is not valid"

    def test_update_baseline_sets_flag(self):
        detector = ModelDriftDetector()
        detector.update_baseline([0.9, 0.8, 0.7])
        assert detector.has_baseline() is True, "detect is not valid"

    def test_check_without_baseline_skips_jsd(self):
        """When no baseline is set, JSD should be None (no JSD check)."""
        detector = ModelDriftDetector(
            js_threshold=0.01,
            confidence_threshold=0.0,
            low_confidence_rate_threshold=1.0,
        )
        result = detector.check([0.9, 0.85, 0.88], epoch=0)
        assert result.js_divergence is None, "Result must not be empty"

    def test_reset_clears_baseline_and_history(self):
        detector = ModelDriftDetector()
        detector.update_baseline([0.9, 0.8])
        detector.check([0.7, 0.6], epoch=1)
        assert detector.has_baseline(), "detect is not valid"
        assert len(detector.history()) == 1, "Collection must not be empty"

        detector.reset()
        assert not detector.has_baseline(), "Condition must be true"
        assert detector.history() == [], "detect is not valid"

    def test_update_baseline_replaces_previous(self):
        detector = ModelDriftDetector()
        detector.update_baseline([0.9] * 10)
        old_dist = detector._baseline_dist[:]
        detector.update_baseline([0.1] * 10)
        assert detector._baseline_dist != old_dist, "_baseline_dist is not valid"

    def test_update_baseline_empty_raises(self):
        detector = ModelDriftDetector()
        with pytest.raises(ValueError, match="non-empty"):
            detector.update_baseline([])


# ---------------------------------------------------------------------------
# T07 — DriftResult.summary() and to_dict()
# ---------------------------------------------------------------------------


class TestDriftResultShape:
    """T07: DriftResult produces correct summary and dict."""

    def _make_result(self, drift: bool) -> DriftResult:
        stats = ConfidenceStats.from_scores([0.8, 0.9, 0.7])
        return DriftResult(
            drift_detected=drift,
            js_divergence=0.12 if drift else 0.02,
            js_threshold=0.05,
            confidence_stats=stats,
            confidence_dropped=drift,
            confidence_threshold=0.5,
            epoch=3,
            reasons=["JSD=0.12 exceeds threshold=0.05"] if drift else [],
        )

    def test_summary_drift(self):
        result = self._make_result(True)
        s = result.summary()
        assert "DRIFT DETECTED" in s, "Condition must be true"
        assert "epoch=3" in s, "Condition must be true"

    def test_summary_no_drift(self):
        result = self._make_result(False)
        s = result.summary()
        assert "No drift detected" in s, "Condition must be true"

    def test_to_dict_keys(self):
        result = self._make_result(True)
        d = result.to_dict()
        expected_keys = {
            "drift_detected",
            "js_divergence",
            "js_threshold",
            "confidence_dropped",
            "confidence_threshold",
            "epoch",
            "reasons",
            "confidence_stats",
        }
        assert expected_keys.issubset(set(d.keys())), "Condition must be true"

    def test_to_dict_values(self):
        result = self._make_result(True)
        d = result.to_dict()
        assert d["drift_detected"] is True, "Condition must be true"
        assert d["epoch"] == 3, "Condition must be true"
        assert isinstance(d["reasons"], list)
        assert isinstance(d["confidence_stats"], dict)


# ---------------------------------------------------------------------------
# T08 — ConfidenceStats.from_scores()
# ---------------------------------------------------------------------------


class TestConfidenceStats:
    """T08: ConfidenceStats computes correct statistics."""

    def test_all_high_confidence(self):
        scores = [0.9, 0.95, 0.85, 0.92, 0.88]
        stats = ConfidenceStats.from_scores(scores, low_conf_threshold=0.5)
        assert stats.mean_confidence == pytest.approx(sum(scores) / len(scores)), "Scores must not be empty"
        assert stats.low_confidence_rate == 0.0, "low_confidence_rate is not valid"
        assert stats.n_samples == 5, "n_samples is not valid"
        assert stats.entropy >= -1e-9, "entropy must be greater than zero"
        assert stats.entropy <= 1.0 + 1e-9, "entropy is not valid"

    def test_all_low_confidence(self):
        scores = [0.1, 0.2, 0.15, 0.18, 0.12]
        stats = ConfidenceStats.from_scores(scores, low_conf_threshold=0.5)
        assert stats.low_confidence_rate == 1.0, "low_confidence_rate is not valid"

    def test_mixed_confidence(self):
        scores = [0.9, 0.9, 0.1, 0.1]
        stats = ConfidenceStats.from_scores(scores, low_conf_threshold=0.5)
        assert stats.low_confidence_rate == pytest.approx(0.5), "low_confidence_rate is not valid"

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            ConfidenceStats.from_scores([])

    def test_to_dict_contains_expected_keys(self):
        stats = ConfidenceStats.from_scores([0.8, 0.6, 0.9])
        d = stats.to_dict()
        for key in (
            "mean_confidence",
            "min_confidence",
            "max_confidence",
            "low_confidence_rate",
            "entropy",
            "n_samples",
        ):
            assert key in d, "Condition must be true"


# ---------------------------------------------------------------------------
# T09 — First epoch auto-sets baseline; second epoch checks drift
# ---------------------------------------------------------------------------


class TestFirstEpochBaseline:
    """T09: check() before baseline returns no JSD; after baseline checks JSD."""

    def test_first_call_no_jsd_then_subsequent_has_jsd(self):
        detector = ModelDriftDetector(
            js_threshold=0.05,
            confidence_threshold=0.0,
            low_confidence_rate_threshold=1.0,
        )
        baseline_scores = [0.9] * 20
        shifted_scores = [0.1] * 20

        # Before baseline
        r0 = detector.check(baseline_scores, epoch=0)
        assert r0.js_divergence is None, "js_divergence is not valid"

        # Manually set baseline (simulating train_loop auto-set)
        detector.update_baseline(baseline_scores)

        # Now drift should be detected
        r1 = detector.check(shifted_scores, epoch=1)
        assert r1.js_divergence is not None, "js_divergence must be initialized"
        assert r1.drift_detected is True, "drift_detected is not valid"


# ---------------------------------------------------------------------------
# T10 — ModelDriftDetector raises ValueError on bad constructor inputs
# ---------------------------------------------------------------------------


class TestModelDriftDetectorValidation:
    """T10: Constructor validates threshold parameters."""

    def test_invalid_js_threshold_zero(self):
        with pytest.raises(ValueError, match="js_threshold"):
            ModelDriftDetector(js_threshold=0.0)

    def test_invalid_js_threshold_over_one(self):
        with pytest.raises(ValueError, match="js_threshold"):
            ModelDriftDetector(js_threshold=1.5)

    def test_invalid_confidence_threshold_negative(self):
        with pytest.raises(ValueError, match="confidence_threshold"):
            ModelDriftDetector(confidence_threshold=-0.1)

    def test_invalid_confidence_threshold_over_one(self):
        with pytest.raises(ValueError, match="confidence_threshold"):
            ModelDriftDetector(confidence_threshold=1.1)

    def test_invalid_n_bins(self):
        with pytest.raises(ValueError, match="n_distribution_bins"):
            ModelDriftDetector(n_distribution_bins=1)

    def test_check_empty_scores_raises(self):
        detector = ModelDriftDetector()
        with pytest.raises(ValueError, match="non-empty"):
            detector.check([], epoch=0)
