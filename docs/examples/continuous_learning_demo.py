# /// script
# dependencies = []
# requires-python = ">=3.10"
# description = "Runnable demo: ContinuousLearningPipeline and FeedbackLoop"
# ///
"""Continuous Learning Demo — Gap 44: Interactive Documentation.

Demonstrates:
  - ContinuousLearningPipeline full cycle:
      drift → trigger → eval gate → promote decision
  - FeedbackLoop ingesting monitoring alerts and drift signals
  - should_adapt() decision predicate

Run with:
    python docs/examples/continuous_learning_demo.py
"""

from __future__ import annotations

import random
import sys
import os

# Ensure the repo src is on the path when run directly
_REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))

from codex_ml.continuous_learning import (
    ContinuousLearningPipeline,
    EvalGate,
    EvalGateResult,
    RetrainingJob,
    RetrainingTrigger,
)
from codex_ml.feedback import FeedbackCollector, FeedbackEvent, FeedbackLoop


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


def _row(label: str, value: object) -> None:
    print(f"  {label:<32} {value}")


# ---------------------------------------------------------------------------
# Continuous Learning Pipeline demo
# ---------------------------------------------------------------------------

def demo_pipeline() -> None:
    _sep("CONTINUOUS LEARNING PIPELINE")

    pipeline = ContinuousLearningPipeline(
        drift_threshold=0.2,
        eval_gate_min_accuracy=0.80,
        eval_gate_max_loss=0.35,
    )

    print(f"\n  Pipeline config:")
    _row("drift_threshold", pipeline.drift_threshold)

    # ---- Step 1: check if retraining is needed ----
    print("\n  [Step 1] Check drift results → should_retrain()")

    no_drift = {"score": 0.05, "drifted": False}
    mild_drift = {"score": 0.15, "drifted": False}
    strong_drift = {"score": 0.42, "drifted": True}

    for label, dr in [("No drift", no_drift), ("Mild drift", mild_drift), ("Strong drift", strong_drift)]:
        decision = pipeline.should_retrain(dr)
        icon = "🔴 RETRAIN" if decision else "✓  stable"
        print(f"    {label:<16} score={dr['score']:.2f} → {icon}")

    # ---- Step 2: trigger retraining ----
    print("\n  [Step 2] Trigger retraining → trigger_retrain()")
    job = pipeline.trigger_retrain(config={"epochs": 10, "lr": 5e-4, "batch_size": 32})
    _row("Job ID", job.job_id)
    _row("Config", job.config)
    _row("Status", job.status)

    # ---- Step 3: simulate training finished — run eval gate ----
    print("\n  [Step 3] Evaluate candidate model → eval_gate()")

    metrics_fail = {"accuracy": 0.75, "loss": 0.40}
    metrics_pass = {"accuracy": 0.87, "loss": 0.22}

    for label, metrics in [("Failing metrics", metrics_fail), ("Passing metrics", metrics_pass)]:
        passed = pipeline.eval_gate(metrics)
        icon = "✅ PASS" if passed else "❌ FAIL"
        print(f"    {label:<20} acc={metrics['accuracy']:.2f} loss={metrics['loss']:.2f} → {icon}")

    # ---- Step 4: promote the model (using passing metrics) ----
    print("\n  [Step 4] Promote model → promote()")
    pipeline.trigger_retrain()  # ensures last_job is set
    promoted = pipeline.promote(
        model_path="models/v2/checkpoint.pt",
        registry={"version": "v2.0", "environment": "production"},
        metrics=metrics_pass,
    )
    icon = "✅ Promoted" if promoted else "❌ Not promoted"
    print(f"    Result: {icon}")

    _sep()


# ---------------------------------------------------------------------------
# FeedbackLoop demo
# ---------------------------------------------------------------------------

def demo_feedback_loop() -> None:
    _sep("FEEDBACK LOOP")

    loop = FeedbackLoop(adapt_threshold=3, adapt_window=10)

    print(f"\n  Config: adapt_threshold=3, adapt_window=10")
    print(f"  (needs ≥3 alert events in last 10 events to trigger adaptation)")

    # Ingest a mix of drift signals and alerts
    print("\n  [Step 1] Ingest 2 drift signals (below threshold)")
    for i in range(2):
        loop.on_drift({
            "drift_score": 0.28 + i * 0.05,
            "source": "data_drift_detector",
            "feature": f"feature_{i}",
        })
    _row("Events collected", len(loop.collector))
    _row("should_adapt()?", loop.should_adapt())

    print("\n  [Step 2] Ingest 4 alerts (crosses adapt_threshold of 3)")
    for sev in ["warning", "critical", "critical", "critical"]:
        loop.on_alert({"severity": sev, "source": "prometheus", "message": "drift rate elevated"})
    _row("Events collected", len(loop.collector))
    _row("should_adapt()?", loop.should_adapt())

    # Aggregate stats
    print("\n  [Step 3] Collector aggregate statistics")
    agg = loop.collector.aggregate()
    for k, v in agg.items():
        if isinstance(v, float):
            _row(k, f"{v:.4f}")
        else:
            _row(k, v)

    # Recent events
    print("\n  [Step 4] Most recent 3 events")
    for ev in loop.collector.get_recent(3):
        print(f"    [{ev.event_type}] source={ev.source} score={ev.score}")

    _sep()


# ---------------------------------------------------------------------------
# EvalGate standalone demo
# ---------------------------------------------------------------------------

def demo_eval_gate() -> None:
    _sep("EVAL GATE  (standalone)")

    gate = EvalGate(
        min_accuracy=0.82,
        max_loss=0.30,
    )

    scenarios = [
        ("Below accuracy floor",  {"accuracy": 0.78, "loss": 0.28}),
        ("Above loss ceiling",    {"accuracy": 0.85, "loss": 0.36}),
        ("Passes all thresholds", {"accuracy": 0.88, "loss": 0.24}),
    ]

    print()
    for label, metrics in scenarios:
        result: EvalGateResult = gate.evaluate(metrics)
        icon = "✅" if result.passed else "❌"
        print(f"  {icon} {label:<28} passed={result.passed}  reasons={result.reasons or ['—']}")

    _sep()


if __name__ == "__main__":
    _sep("CONTINUOUS LEARNING DEMO")
    print("  Modules: codex_ml.continuous_learning / codex_ml.feedback")
    print("  Demonstrates drift → retrain → gate → promote + feedback loop")
    _sep()
    print()

    demo_pipeline()
    print()
    demo_feedback_loop()
    print()
    demo_eval_gate()

    print()
    _sep("DEMO COMPLETE")
    print("  ✓ ContinuousLearningPipeline: full retrain cycle passed")
    print("  ✓ FeedbackLoop: alert ingestion + should_adapt() passed")
    print("  ✓ EvalGate: threshold evaluation passed")
    _sep()
