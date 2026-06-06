# /// script
# dependencies = []
# requires-python = ">=3.10"
# description = "Runnable demo: DataDriftDetector and ModelDriftDetector"
# ///
"""Drift Detection Demo — Gap 44: Interactive Documentation.

Demonstrates:
  - Generating synthetic reference and drifted distributions
  - Running DataDriftDetector (PSI + KL divergence)
  - Running ModelDriftDetector (Jensen-Shannon divergence + confidence stats)
  - Printing a formatted drift report with scores, thresholds, and decisions

Run with:
    python docs/examples/drift_detection_demo.py
"""

from __future__ import annotations

import random
import sys
import os

# Ensure the repo src is on the path when run directly
_REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))

from codex_ml.monitoring.data_drift import DataDriftDetector, DriftResult
from codex_ml.monitoring.model_drift import ModelDriftDetector


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sep(title: str = "") -> None:
    line = "=" * 60
    if title:
        pad = (60 - len(title) - 2) // 2
        print(f"{'=' * pad} {title} {'=' * (60 - pad - len(title) - 2)}")
    else:
        print(line)


def _row(label: str, value: object) -> None:
    print(f"  {label:<28} {value}")


def _generate_stable_distribution(n_bins: int = 8, seed: int = 42) -> list[float]:
    """Stable reference distribution — roughly uniform with slight noise."""
    rng = random.Random(seed)
    raw = [1.0 / n_bins + rng.gauss(0, 0.01) for _ in range(n_bins)]
    total = sum(raw)
    return [max(v / total, 1e-6) for v in raw]


def _generate_drifted_distribution(reference: list[float], shift: float = 0.4, seed: int = 99) -> list[float]:
    """Drifted distribution — mass shifted toward the tail bins."""
    rng = random.Random(seed)
    n = len(reference)
    raw = list(reference)
    # move probability mass from first half to second half
    for i in range(n // 2):
        transfer = raw[i] * shift * rng.uniform(0.8, 1.2)
        transfer = min(transfer, raw[i] - 1e-6)
        raw[i] -= transfer
        raw[n - 1 - i] += transfer
    total = sum(raw)
    return [max(v / total, 1e-6) for v in raw]


def _generate_confidence_scores(n: int = 200, mean: float = 0.85, std: float = 0.05, seed: int = 7) -> list[float]:
    rng = random.Random(seed)
    return [max(0.0, min(1.0, rng.gauss(mean, std))) for _ in range(n)]


# ---------------------------------------------------------------------------
# Main demo
# ---------------------------------------------------------------------------

def demo_data_drift() -> None:
    _sep("DATA DRIFT DETECTION (PSI + KL Divergence)")

    reference = _generate_stable_distribution(n_bins=8)
    stable_current = _generate_stable_distribution(n_bins=8, seed=43)  # similar to reference
    drifted_current = _generate_drifted_distribution(reference, shift=0.45)

    detector = DataDriftDetector(psi_threshold=0.2, kl_threshold=0.5)

    print("\n  Reference distribution (8 bins):")
    print("  " + "  ".join(f"{v:.3f}" for v in reference))

    print("\n  [Scenario A] Current ≈ Reference (no drift expected)")
    psi_a = detector.detect_psi(reference, stable_current)
    kl_a = detector.detect_kl(reference, stable_current)
    _row("PSI score", f"{psi_a.score:.4f}  (threshold={psi_a.threshold})")
    _row("PSI drifted?", psi_a.drifted)
    _row("KL score", f"{kl_a.score:.4f}  (threshold={kl_a.threshold})")
    _row("KL drifted?", kl_a.drifted)

    print("\n  [Scenario B] Current ≠ Reference (drift expected)")
    psi_b = detector.detect_psi(reference, drifted_current)
    kl_b = detector.detect_kl(reference, drifted_current)
    _row("PSI score", f"{psi_b.score:.4f}  (threshold={psi_b.threshold})")
    _row("PSI drifted?", psi_b.drifted)
    _row("KL score", f"{kl_b.score:.4f}  (threshold={kl_b.threshold})")
    _row("KL drifted?", kl_b.drifted)

    # check_epoch convenience wrapper
    print("\n  [check_epoch] Multi-feature epoch check:")
    features = {
        "feature_age": (reference, stable_current),
        "feature_income": (reference, drifted_current),
    }
    for feat, (ref, cur) in features.items():
        epoch_results = detector.check_epoch(ref, cur)
        any_drift = any(r.drifted for r in epoch_results)
        print(f"    {feat}: {'⚠ DRIFT' if any_drift else '✓ stable'}")

    _sep()


def demo_model_drift() -> None:
    _sep("MODEL DRIFT DETECTION (Jensen-Shannon + Confidence)")

    baseline_scores = _generate_confidence_scores(n=300, mean=0.88, std=0.05, seed=1)
    stable_scores = _generate_confidence_scores(n=200, mean=0.86, std=0.06, seed=2)
    drifted_scores = _generate_confidence_scores(n=200, mean=0.55, std=0.18, seed=3)

    detector = ModelDriftDetector(js_threshold=0.05, confidence_threshold=0.6)
    detector.update_baseline(baseline_scores)

    print(f"\n  Baseline set: {len(baseline_scores)} confidence scores")
    print(f"  JS threshold:           {detector._js_threshold}")
    print(f"  Confidence threshold:   {detector._confidence_threshold}")

    print("\n  [Scenario A] Current epoch ≈ Baseline (no drift expected)")
    result_a = detector.check(stable_scores)
    _row("Drift detected?", result_a.drift_detected)
    _row("JS divergence", f"{result_a.js_divergence:.4f}")
    _row("Mean confidence", f"{result_a.confidence.mean:.4f}")
    _row("Low-conf rate", f"{result_a.confidence.low_confidence_rate:.4f}")
    print(f"  Summary: {result_a.summary()}")

    print("\n  [Scenario B] Degraded epoch (drift expected)")
    result_b = detector.check(drifted_scores)
    _row("Drift detected?", result_b.drift_detected)
    _row("JS divergence", f"{result_b.js_divergence:.4f}")
    _row("Mean confidence", f"{result_b.confidence.mean:.4f}")
    _row("Low-conf rate", f"{result_b.confidence.low_confidence_rate:.4f}")
    print(f"  Summary: {result_b.summary()}")

    _sep()


if __name__ == "__main__":
    _sep("DRIFT DETECTION DEMO")
    print("  Module: codex_ml.monitoring.data_drift / model_drift")
    print("  All computations use pure-Python (no heavy dependencies)")
    _sep()
    print()

    demo_data_drift()
    print()
    demo_model_drift()

    print()
    _sep("DEMO COMPLETE")
    print("  ✓ DataDriftDetector: PSI + KL divergence checks passed")
    print("  ✓ ModelDriftDetector: JS divergence + confidence checks passed")
    _sep()
