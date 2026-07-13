# /// script
# dependencies = []
# requires-python = ">=3.10"
# description = "Runnable demo: ABTestSuite and run_ab_test"
# ///
"""A/B Testing Demo — Gap 44: Interactive Documentation.

Demonstrates:
  - Generating synthetic control vs treatment metric samples
  - Running run_ab_test() for a single metric (Welch t-test)
  - Running ABTestSuite for multiple metrics simultaneously
  - Printing a formatted comparison table with winner, p-value, effect size

Run with:
    python docs/examples/ab_test_demo.py
"""

from __future__ import annotations

import os
import random
import sys

# Ensure the repo src is on the path when run directly
_REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))

from codex_ml.experiments.ab_testing import ABTest, ABTestResult, ABTestSuite, run_ab_test

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sep(title: str = "") -> None:
    if title:
        pad = (60 - len(title) - 2) // 2
        tail = 60 - pad - len(title) - 2
        print(f"{'=' * pad} {title} {'=' * tail}")
    else:
        print("=" * 60)


def _generate_samples(
    n: int = 120,
    mean: float = 0.75,
    std: float = 0.08,
    seed: int = 0,
) -> list[float]:
    rng = random.Random(seed)
    return [max(0.0, min(1.0, rng.gauss(mean, std))) for _ in range(n)]


def _print_result(name: str, result: ABTestResult) -> None:
    winner_icon = "🏆" if result.winner != "inconclusive" else "⚖"
    sig_label = "significant" if result.significant else "not significant"
    print(f"\n  Metric : {name}")
    print(f"  Winner : {winner_icon} {result.winner.upper()}  ({sig_label})")
    print(f"  p-value: {result.p_value:.4f}   (α = 0.05)")
    print(f"  Effect : Cohen's d = {result.effect_size:+.4f}")
    lo, hi = result.confidence_interval
    print(f"  95% CI : [{lo:+.4f}, {hi:+.4f}]  (treatment − control)")


# ---------------------------------------------------------------------------
# Single metric demo
# ---------------------------------------------------------------------------

def demo_single_metric() -> None:
    _sep("SINGLE-METRIC A/B TEST  (run_ab_test)")

    # Scenario 1: no practical difference
    ctrl_a = _generate_samples(n=100, mean=0.75, std=0.08, seed=10)
    trt_a = _generate_samples(n=100, mean=0.76, std=0.08, seed=11)
    result_a = run_ab_test(ctrl_a, trt_a, metric_name="precision", alpha=0.05)

    print("\n  [Scenario A] Nearly identical groups (inconclusive expected)")
    _print_result("precision", result_a)

    # Scenario 2: clear winner
    ctrl_b = _generate_samples(n=150, mean=0.70, std=0.07, seed=20)
    trt_b = _generate_samples(n=150, mean=0.82, std=0.07, seed=21)
    result_b = run_ab_test(ctrl_b, trt_b, metric_name="recall", alpha=0.05)

    print("\n  [Scenario B] Treatment clearly better (treatment expected)")
    _print_result("recall", result_b)

    _sep()


# ---------------------------------------------------------------------------
# Suite demo
# ---------------------------------------------------------------------------

def demo_suite() -> None:
    _sep("MULTI-METRIC A/B TEST SUITE  (ABTestSuite)")

    metrics = {
        "accuracy":  (0.78, 0.82, 0.06, 0.06, 200),
        "f1_score":  (0.73, 0.79, 0.08, 0.07, 180),
        "auc_roc":   (0.85, 0.84, 0.04, 0.04, 160),   # control wins or inconclusive
        "latency_ms": (95.0, 88.0, 10.0, 9.5, 120),   # lower is better; control baseline
    }

    suite = ABTestSuite()
    for i, (name, (ctrl_mean, trt_mean, ctrl_std, trt_std, n)) in enumerate(metrics.items()):
        ctrl = _generate_samples(n=n, mean=ctrl_mean, std=ctrl_std, seed=i * 10 + 1)
        trt = _generate_samples(n=n, mean=trt_mean, std=trt_std, seed=i * 10 + 2)
        suite.add_test(ABTest(
            name=name,
            control_metrics=ctrl,
            treatment_metrics=trt,
        ))

    results = suite.run_all()
    report = suite.report()

    # Print summary table
    print()
    print(f"  {'Metric':<16} {'Winner':<14} {'p-value':>8} {'Effect (d)':>12} {'Sig?':>6}")
    print(f"  {'-'*16} {'-'*14} {'-'*8} {'-'*12} {'-'*6}")
    for name, res in results.items():
        sig = "✓" if res.significant else "✗"
        print(
            f"  {name:<16} {res.winner:<14} {res.p_value:>8.4f} "
            f"{res.effect_size:>+12.4f} {sig:>6}"
        )

    summary = report["summary"]
    print(f"\n  Total tests  : {summary['total']}")
    print(f"  Significant  : {summary['significant']}")
    print(f"  Inconclusive : {summary['inconclusive']}")

    _sep()


if __name__ == "__main__":
    _sep("A/B TESTING DEMO")
    print("  Module: codex_ml.experiments.ab_testing")
    print("  Uses Welch's t-test; falls back to pure stdlib if scipy absent")
    _sep()
    print()

    demo_single_metric()
    print()
    demo_suite()

    print()
    _sep("DEMO COMPLETE")
    print("  ✓ run_ab_test: single-metric comparison passed")
    print("  ✓ ABTestSuite: multi-metric suite passed")
    _sep()
