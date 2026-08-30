"""Data drift monitoring using PSI and KL-divergence detectors.

This module provides ``DataDriftDetector``, a lightweight, dependency-free
drift detector that can be used to compare reference and current feature
distributions at the end of every training epoch.

Usage example::

    from codex_ml.monitoring.data_drift import DataDriftDetector

    detector = DataDriftDetector(psi_threshold=0.2, kl_threshold=0.5)
    reference = [0.1, 0.4, 0.3, 0.2]   # reference distribution (must sum ≤ 1)
    current   = [0.15, 0.35, 0.3, 0.2]  # current distribution

    psi_result = detector.detect_psi(reference, current)
    kl_result  = detector.detect_kl(reference, current)

    if psi_result.drifted:
        logger.info(f"PSI drift detected: score={psi_result.score:.4f}")
    if kl_result.drifted:
        logger.info(f"KL  drift detected: score={kl_result.score:.4f}")

Implementation notes
--------------------
* **No external dependencies.** Only the standard library is required.
  ``numpy`` / ``scipy`` are used *opportunistically* when available so the
  module remains importable in minimal environments.
* Both ``detect_psi`` and ``detect_kl`` accept plain Python sequences
  (list, tuple, …) as well as numpy arrays.
* Input distributions are *automatically normalised* to sum to 1 and
  *epsilon-smoothed* to avoid division-by-zero / log(0) issues.

PSI interpretation
------------------
| PSI value  | Interpretation               |
|------------|------------------------------|
| < 0.1      | No significant change        |
| 0.1 – 0.2  | Slight change — monitor      |
| > 0.2      | Significant change — act     |

KL-divergence interpretation
-----------------------------
| KL value   | Interpretation               |
|------------|------------------------------|
| < 0.1      | Distributions are very close |
| 0.1 – 0.5  | Moderate divergence          |
| > 0.5      | Strong divergence            |
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Sequence

from codex.logging.structured_logger import logger

logger = logging.getLogger(__name__)

__all__ = [
    "DataDriftDetector",
    "DriftResult",
]

_EPSILON = 1e-8  # smoothing constant to avoid log(0) / div-by-zero


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class DriftResult:
    """Container for a single drift detection result.

    Attributes:
        method: Drift detection method used (``"psi"`` or ``"kl"``).
        score: Computed drift score (lower is better).
        threshold: Threshold above which drift is flagged.
        drifted: ``True`` when ``score > threshold``.
        severity: One of ``"none"``, ``"slight"``, or ``"significant"``.
        details: Extra diagnostic information (bin-level breakdown, etc.).
        detected_at: ISO-8601 timestamp of detection.
    """

    method: str
    score: float
    threshold: float
    drifted: bool
    severity: str
    details: dict[str, Any] = field(default_factory=dict)
    detected_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Serialise the result to a plain dictionary."""
        return {
            "method": self.method,
            "score": self.score,
            "threshold": self.threshold,
            "drifted": self.drifted,
            "severity": self.severity,
            "details": self.details,
            "detected_at": self.detected_at,
        }


# ---------------------------------------------------------------------------
# Core detector
# ---------------------------------------------------------------------------


class DataDriftDetector:
    """Detect data distribution drift using PSI and KL-divergence.

    Parameters
    ----------
    psi_threshold:
        PSI score above which drift is flagged (default ``0.2``).
    kl_threshold:
        KL-divergence above which drift is flagged (default ``0.5``).
    epsilon:
        Smoothing constant added to each bin to avoid log(0) and
        division-by-zero (default ``1e-8``).
    """

    def __init__(
        self,
        psi_threshold: float = 0.2,
        kl_threshold: float = 0.5,
        epsilon: float = _EPSILON,
    ) -> None:
        if psi_threshold <= 0:
            raise ValueError(f"psi_threshold must be positive, got {psi_threshold}")
        if kl_threshold <= 0:
            raise ValueError(f"kl_threshold must be positive, got {kl_threshold}")
        if epsilon <= 0:
            raise ValueError(f"epsilon must be positive, got {epsilon}")

        self.psi_threshold = psi_threshold
        self.kl_threshold = kl_threshold
        self.epsilon = epsilon

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect_psi(
        self,
        reference: Sequence[float],
        current: Sequence[float],
        feature_name: str = "feature",
    ) -> DriftResult:
        """Compute the Population Stability Index (PSI) between two distributions.

        PSI = Σ (current_i − reference_i) × ln(current_i / reference_i)

        Parameters
        ----------
        reference:
            The reference (baseline) distribution.  Values are normalised
            and smoothed automatically.
        current:
            The current distribution to compare against the reference.
        feature_name:
            Optional label used in diagnostic details.

        Returns
        -------
        DriftResult
            Populated result including per-bin breakdown.

        Raises
        ------
        ValueError
            If the inputs have different lengths or are empty.
        """
        ref, cur = self._validate_and_normalise(reference, current, "PSI")

        bin_scores: list[float] = []
        for r, c in zip(ref, cur):
            bin_psi = (c - r) * math.log(c / r)
            bin_scores.append(bin_psi)

        psi_score = sum(bin_scores)

        severity = self._psi_severity(psi_score)
        drifted = psi_score > self.psi_threshold

        if drifted:
            logger.warning(
                "PSI drift detected for '%s': score=%.4f (threshold=%.4f, severity=%s)",
                feature_name,
                psi_score,
                self.psi_threshold,
                severity,
            )
        else:
            logger.debug(
                "PSI check for '%s': score=%.4f (no drift)",
                feature_name,
                psi_score,
            )

        return DriftResult(
            method="psi",
            score=psi_score,
            threshold=self.psi_threshold,
            drifted=drifted,
            severity=severity,
            details={
                "feature_name": feature_name,
                "num_bins": len(ref),
                "bin_scores": bin_scores,
                "reference_dist": list(ref),
                "current_dist": list(cur),
            },
        )

    def detect_kl(
        self,
        reference: Sequence[float],
        current: Sequence[float],
        feature_name: str = "feature",
    ) -> DriftResult:
        """Compute the KL-divergence D_KL(current ‖ reference).

        KL(P ‖ Q) = Σ P(i) × ln(P(i) / Q(i))

        Here *P* is the **current** distribution and *Q* is the **reference**.

        Parameters
        ----------
        reference:
            The reference (baseline) distribution.
        current:
            The current distribution.
        feature_name:
            Optional label used in diagnostic details.

        Returns
        -------
        DriftResult
            Populated result including per-bin breakdown.

        Raises
        ------
        ValueError
            If the inputs have different lengths or are empty.
        """
        ref, cur = self._validate_and_normalise(reference, current, "KL")

        bin_scores: list[float] = []
        for r, c in zip(ref, cur):
            # KL(current ‖ reference) — current is P, reference is Q
            bin_kl = c * math.log(c / r)
            bin_scores.append(bin_kl)

        kl_score = sum(bin_scores)

        severity = self._kl_severity(kl_score)
        drifted = kl_score > self.kl_threshold

        if drifted:
            logger.warning(
                "KL drift detected for '%s': score=%.4f (threshold=%.4f, severity=%s)",
                feature_name,
                kl_score,
                self.kl_threshold,
                severity,
            )
        else:
            logger.debug(
                "KL check for '%s': score=%.4f (no drift)",
                feature_name,
                kl_score,
            )

        return DriftResult(
            method="kl",
            score=kl_score,
            threshold=self.kl_threshold,
            drifted=drifted,
            severity=severity,
            details={
                "feature_name": feature_name,
                "num_bins": len(ref),
                "bin_scores": bin_scores,
                "reference_dist": list(ref),
                "current_dist": list(cur),
            },
        )

    def check_epoch(
        self,
        reference: Sequence[float],
        current: Sequence[float],
        epoch: int = 0,
        feature_name: str = "feature",
    ) -> dict[str, DriftResult]:
        """Run both PSI and KL checks for a single epoch.

        This is a convenience wrapper intended to be called from the training
        loop after the performance monitor block.

        Parameters
        ----------
        reference:
            Reference distribution.
        current:
            Current epoch distribution.
        epoch:
            Training epoch number (used for logging context).
        feature_name:
            Name label for diagnostics.

        Returns
        -------
        dict[str, DriftResult]
            Mapping with keys ``"psi"`` and ``"kl"``.
        """
        logger.debug("Running data drift checks for epoch %d / feature '%s'", epoch, feature_name)
        psi_result = self.detect_psi(reference, current, feature_name=feature_name)
        kl_result = self.detect_kl(reference, current, feature_name=feature_name)

        any_drift = psi_result.drifted or kl_result.drifted
        if any_drift:
            logger.warning(
                "Data drift detected at epoch %d (psi=%.4f, kl=%.4f)",
                epoch,
                psi_result.score,
                kl_result.score,
            )

        return {"psi": psi_result, "kl": kl_result}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_and_normalise(
        self,
        reference: Sequence[float],
        current: Sequence[float],
        method: str,
    ) -> tuple[list[float], list[float]]:
        """Validate inputs, normalise, and apply epsilon smoothing.

        Returns
        -------
        tuple[list[float], list[float]]
            ``(ref_normalised, cur_normalised)`` — both sum to ≈ 1.
        """
        if len(reference) == 0 or len(current) == 0:
            raise ValueError(f"{method}: input distributions must not be empty")
        if len(reference) != len(current):
            raise ValueError(
                f"{method}: reference and current distributions must have the same length "
                f"(got {len(reference)} vs {len(current)})"
            )

        ref_list = [float(v) for v in reference]
        cur_list = [float(v) for v in current]

        # Epsilon smoothing — ensures no zero bins
        ref_list = [v + self.epsilon for v in ref_list]
        cur_list = [v + self.epsilon for v in cur_list]

        # Normalise to a proper probability distribution
        ref_sum = sum(ref_list)
        cur_sum = sum(cur_list)
        ref_list = [v / ref_sum for v in ref_list]
        cur_list = [v / cur_sum for v in cur_list]

        return ref_list, cur_list

    # ------------------------------------------------------------------
    # Severity helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _psi_severity(score: float) -> str:
        """Return a human-readable PSI severity label."""
        if score < 0.1:
            return "none"
        if score < 0.2:
            return "slight"
        return "significant"

    @staticmethod
    def _kl_severity(score: float) -> str:
        """Return a human-readable KL severity label."""
        if score < 0.1:
            return "none"
        if score < 0.5:
            return "moderate"
        return "significant"
