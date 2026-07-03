"""Model Drift Detection Module (Gap 18).

Implements concept-drift detection for ML models using:
- Jensen-Shannon divergence for output distribution shift
- Prediction confidence monitoring (mean, entropy, low-confidence rate)

Designed for post-epoch wiring inside ``train_loop.py`` alongside the
existing ``PerformanceMonitor``.  All public classes are pure-Python with
no hard PyTorch / NumPy dependency — they work with plain ``list[float]``
inputs so they can run in CPU-only CI environments.

Usage
-----
>>> detector = ModelDriftDetector(js_threshold=0.05, confidence_threshold=0.4)
>>> detector.update_baseline(reference_probs)       # call once on baseline epoch
>>> result = detector.check(current_probs)          # call every post-epoch
>>> if result.drift_detected:
...     logger.info(result.summary())

Classes
-------
- ``ConfidenceStats``      — per-epoch confidence summary
- ``DriftResult``          — result returned by ``ModelDriftDetector.check()``
- ``ModelDriftDetector``   — main detector class (Gap 18 entry point)
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Optional

from codex.logging.structured_logger import logger

logger = logging.getLogger(__name__)

__all__ = [
    "ConfidenceStats",
    "DriftResult",
    "ModelDriftDetector",
    "jensen_shannon_divergence",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_LOG2 = math.log(2)


def _kl_divergence(p: list[float], q: list[float]) -> float:
    """Compute KL(P || Q).

    Distributions are assumed to be normalised (sum ≈ 1).  Zero entries in
    *q* are guarded with a small epsilon to avoid division-by-zero / -inf.
    """
    if len(p) != len(q):
        raise ValueError(f"p and q must have the same length, got {len(p)} vs {len(q)}")
    eps = 1e-12
    total = 0.0
    for pi, qi in zip(p, q):
        if pi <= 0.0:
            continue
        qi_safe = max(qi, eps)
        total += pi * math.log(pi / qi_safe)
    return total


def jensen_shannon_divergence(p: list[float], q: list[float]) -> float:
    """Compute the Jensen-Shannon divergence between two distributions.

    JSD(P || Q) = 0.5 * KL(P || M) + 0.5 * KL(Q || M)
    where M = 0.5 * (P + Q).

    Parameters
    ----------
    p, q:
        Probability vectors of equal length.  Need not be exactly normalised;
        they are re-normalised internally.

    Returns
    -------
    float
        JSD value in the range [0, 1] (using base-2 logarithm).
    """
    if len(p) != len(q):
        raise ValueError(f"p and q must have the same length, got {len(p)} vs {len(q)}")
    n = len(p)
    if n == 0:
        raise ValueError("p and q must be non-empty")

    # Re-normalise to guard against small floating-point rounding errors.
    sum_p = sum(p)
    sum_q = sum(q)
    if sum_p <= 0 or sum_q <= 0:
        raise ValueError("Distributions must have positive mass")

    p_norm = [x / sum_p for x in p]
    q_norm = [x / sum_q for x in q]

    m = [0.5 * (pi + qi) for pi, qi in zip(p_norm, q_norm)]

    jsd = 0.5 * _kl_divergence(p_norm, m) + 0.5 * _kl_divergence(q_norm, m)
    # Normalise to [0, 1] (base-2 logarithm convention)
    jsd_base2 = jsd / _LOG2
    # Clamp to [0, 1] to handle floating-point noise near boundaries.
    return max(0.0, min(1.0, jsd_base2))


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


@dataclass
class ConfidenceStats:
    """Summary statistics for a batch of per-sample confidence scores.

    Parameters
    ----------
    scores:
        Iterable of confidence values in [0, 1], one per prediction.
    low_conf_threshold:
        Samples below this value are counted as "low-confidence".
    """

    mean_confidence: float
    min_confidence: float
    max_confidence: float
    low_confidence_rate: float  # fraction of samples below threshold
    entropy: float  # normalised entropy of the confidence distribution
    n_samples: int

    @classmethod
    def from_scores(
        cls,
        scores: list[float],
        low_conf_threshold: float = 0.5,
    ) -> "ConfidenceStats":
        """Compute statistics from a list of confidence scores."""
        if not scores:
            raise ValueError("scores must be non-empty")

        n = len(scores)
        mean_conf = sum(scores) / n
        min_conf = min(scores)
        max_conf = max(scores)
        low_conf_rate = sum(1 for s in scores if s < low_conf_threshold) / n

        # Entropy of the empirical distribution over a histogram (8 bins).
        num_bins = min(8, n)
        bins = [0] * num_bins
        for s in scores:
            idx = min(int(s * num_bins), num_bins - 1)
            bins[idx] += 1
        probs = [b / n for b in bins]
        ent = -sum(p * math.log(p + 1e-12) for p in probs if p > 0)
        # Normalise to [0, 1] using max entropy = log(num_bins)
        max_ent = math.log(num_bins)
        norm_entropy = ent / max_ent if max_ent > 0 else 0.0

        return cls(
            mean_confidence=mean_conf,
            min_confidence=min_conf,
            max_confidence=max_conf,
            low_confidence_rate=low_conf_rate,
            entropy=norm_entropy,
            n_samples=n,
        )

    def to_dict(self) -> dict[str, float]:
        return {
            "mean_confidence": self.mean_confidence,
            "min_confidence": self.min_confidence,
            "max_confidence": self.max_confidence,
            "low_confidence_rate": self.low_confidence_rate,
            "entropy": self.entropy,
            "n_samples": float(self.n_samples),
        }


@dataclass
class DriftResult:
    """Result of a single drift check.

    Attributes
    ----------
    drift_detected:
        ``True`` when any monitored metric exceeds its threshold.
    js_divergence:
        Jensen-Shannon divergence between current and baseline output
        distributions.  ``None`` when no baseline is set.
    js_threshold:
        Threshold used for the JSD check.
    confidence_stats:
        Per-epoch confidence statistics for the current distribution.
    confidence_dropped:
        ``True`` when the mean confidence has dropped below
        ``confidence_threshold``.
    confidence_threshold:
        Threshold used for the confidence check.
    epoch:
        Epoch number associated with this result (informational).
    reasons:
        Human-readable list of triggered drift signals.
    """

    drift_detected: bool
    js_divergence: Optional[float]
    js_threshold: float
    confidence_stats: Optional[ConfidenceStats]
    confidence_dropped: bool
    confidence_threshold: float
    epoch: int
    reasons: list[str] = field(default_factory=list)

    def summary(self) -> str:
        """Return a one-line human-readable summary."""
        if not self.drift_detected:
            return f"[epoch={self.epoch}] No drift detected."
        return f"[epoch={self.epoch}] DRIFT DETECTED — " + "; ".join(self.reasons)

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "drift_detected": self.drift_detected,
            "js_divergence": self.js_divergence,
            "js_threshold": self.js_threshold,
            "confidence_dropped": self.confidence_dropped,
            "confidence_threshold": self.confidence_threshold,
            "epoch": self.epoch,
            "reasons": self.reasons,
        }
        if self.confidence_stats is not None:
            out["confidence_stats"] = self.confidence_stats.to_dict()
        return out


# ---------------------------------------------------------------------------
# Main detector
# ---------------------------------------------------------------------------


class ModelDriftDetector:
    """Concept-drift detector for model output distributions.

    Monitors two complementary signals every epoch:

    1. **Output-distribution shift** via Jensen-Shannon divergence between
       the current epoch's softmax output histogram and a stored baseline.
    2. **Prediction-confidence degradation** — alerts when the mean per-
       sample confidence drops below ``confidence_threshold`` or when the
       low-confidence rate exceeds ``low_confidence_rate_threshold``.

    Parameters
    ----------
    js_threshold:
        JSD value (0–1) above which distribution shift is declared.
        Default is 0.05 (5 % of the maximum possible divergence).
    confidence_threshold:
        Mean confidence below which a confidence-drop alert is raised.
        Default is 0.5.
    low_confidence_rate_threshold:
        Fraction of low-confidence predictions above which an alert is
        raised.  Default is 0.3.
    low_conf_score_cutoff:
        Per-sample confidence value below which a sample is deemed
        "low-confidence".  Default is 0.5.
    n_distribution_bins:
        Number of histogram bins used to discretise the output distribution
        for JSD computation.  Default is 10.

    Example
    -------
    >>> import math
    >>> detector = ModelDriftDetector(js_threshold=0.05)
    >>> baseline_probs = [0.9, 0.8, 0.85, 0.95, 0.7]
    >>> detector.update_baseline(baseline_probs)
    >>> result = detector.check([0.3, 0.2, 0.4, 0.35, 0.25], epoch=5)
    >>> result.drift_detected
    True
    """

    def __init__(
        self,
        js_threshold: float = 0.05,
        confidence_threshold: float = 0.5,
        low_confidence_rate_threshold: float = 0.3,
        low_conf_score_cutoff: float = 0.5,
        n_distribution_bins: int = 10,
    ) -> None:
        if not (0.0 < js_threshold <= 1.0):
            raise ValueError(f"js_threshold must be in (0, 1], got {js_threshold}")
        if not (0.0 <= confidence_threshold <= 1.0):
            raise ValueError(f"confidence_threshold must be in [0, 1], got {confidence_threshold}")
        if not (0.0 <= low_confidence_rate_threshold <= 1.0):
            raise ValueError(
                f"low_confidence_rate_threshold must be in [0, 1], "
                f"got {low_confidence_rate_threshold}"
            )
        if n_distribution_bins < 2:
            raise ValueError(f"n_distribution_bins must be >= 2, got {n_distribution_bins}")

        self.js_threshold = js_threshold
        self.confidence_threshold = confidence_threshold
        self.low_confidence_rate_threshold = low_confidence_rate_threshold
        self.low_conf_score_cutoff = low_conf_score_cutoff
        self.n_distribution_bins = n_distribution_bins

        self._baseline_dist: Optional[list[float]] = None
        self._history: list[DriftResult] = []

    # ------------------------------------------------------------------
    # Baseline management
    # ------------------------------------------------------------------

    def update_baseline(self, confidence_scores: list[float]) -> None:
        """Set (or replace) the reference distribution from *confidence_scores*.

        Parameters
        ----------
        confidence_scores:
            List of per-sample confidence values in [0, 1] from the baseline
            epoch (e.g. epoch 0 or a clean validation set).
        """
        if not confidence_scores:
            raise ValueError("confidence_scores must be non-empty")
        self._baseline_dist = self._to_histogram(confidence_scores)
        logger.info(
            "ModelDriftDetector: baseline updated from %d samples",
            len(confidence_scores),
        )

    def has_baseline(self) -> bool:
        """Return ``True`` if a baseline distribution is stored."""
        return self._baseline_dist is not None

    # ------------------------------------------------------------------
    # Core check
    # ------------------------------------------------------------------

    def check(
        self,
        confidence_scores: list[float],
        epoch: int = 0,
    ) -> DriftResult:
        """Check current epoch outputs for concept drift.

        Parameters
        ----------
        confidence_scores:
            Per-sample confidence values in [0, 1] for the current epoch.
        epoch:
            Current epoch index (used in the returned ``DriftResult``).

        Returns
        -------
        DriftResult
            Detailed result including whether drift was detected and why.
        """
        if not confidence_scores:
            raise ValueError("confidence_scores must be non-empty")

        reasons: list[str] = []
        drift_detected = False
        js_div: Optional[float] = None
        confidence_dropped = False

        # 1. Confidence statistics
        stats = ConfidenceStats.from_scores(
            confidence_scores, low_conf_threshold=self.low_conf_score_cutoff
        )

        # 2. Jensen-Shannon divergence (only if baseline is available)
        if self._baseline_dist is not None:
            current_dist = self._to_histogram(confidence_scores)
            js_div = jensen_shannon_divergence(self._baseline_dist, current_dist)
            if js_div > self.js_threshold:
                reasons.append(f"JSD={js_div:.4f} exceeds threshold={self.js_threshold:.4f}")
                drift_detected = True

        # 3. Confidence drop check
        if stats.mean_confidence < self.confidence_threshold:
            confidence_dropped = True
            reasons.append(
                f"mean_confidence={stats.mean_confidence:.4f} < "
                f"threshold={self.confidence_threshold:.4f}"
            )
            drift_detected = True

        # 4. Low-confidence rate check
        if stats.low_confidence_rate > self.low_confidence_rate_threshold:
            confidence_dropped = True
            reasons.append(
                f"low_confidence_rate={stats.low_confidence_rate:.4f} > "
                f"threshold={self.low_confidence_rate_threshold:.4f}"
            )
            drift_detected = True

        result = DriftResult(
            drift_detected=drift_detected,
            js_divergence=js_div,
            js_threshold=self.js_threshold,
            confidence_stats=stats,
            confidence_dropped=confidence_dropped,
            confidence_threshold=self.confidence_threshold,
            epoch=epoch,
            reasons=reasons,
        )

        self._history.append(result)

        if drift_detected:
            logger.warning("ModelDriftDetector: %s", result.summary())
        else:
            logger.debug("ModelDriftDetector: %s", result.summary())

        return result

    # ------------------------------------------------------------------
    # History / utilities
    # ------------------------------------------------------------------

    def history(self) -> list[DriftResult]:
        """Return all ``DriftResult`` objects produced so far."""
        return list(self._history)

    def reset_history(self) -> None:
        """Clear recorded history (baseline is preserved)."""
        self._history.clear()

    def reset(self) -> None:
        """Clear both history and baseline."""
        self._history.clear()
        self._baseline_dist = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _to_histogram(self, scores: list[float]) -> list[float]:
        """Discretise *scores* into a normalised histogram.

        Values are clipped to [0, 1] before binning.
        """
        n_bins = self.n_distribution_bins
        counts = [0.0] * n_bins
        for s in scores:
            s_clipped = max(0.0, min(1.0, s))
            idx = min(int(s_clipped * n_bins), n_bins - 1)
            counts[idx] += 1.0
        total = sum(counts)
        if total == 0:
            # Uniform fallback (should never happen with non-empty input)
            return [1.0 / n_bins] * n_bins
        return [c / total for c in counts]
