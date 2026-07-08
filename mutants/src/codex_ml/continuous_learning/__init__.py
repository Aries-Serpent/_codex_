"""Continuous learning pipeline for Codex ML.

This package implements a drift-triggered retraining loop that:

1. Detects when model or data drift exceeds a configurable threshold.
2. Creates a :class:`RetrainingTrigger` descriptor capturing the drift event.
3. Runs the model through an :class:`EvalGate` to verify quality before
   promoting it to production.

Quick start::

    from codex_ml.continuous_learning import (
        ContinuousLearningPipeline,
        RetrainingTrigger,
        EvalGate,
    )

    pipeline = ContinuousLearningPipeline(
        drift_threshold=0.2,
        eval_gate_min_accuracy=0.80,
    )
    if pipeline.should_retrain({"score": 0.35, "drifted": True}):
        job = pipeline.trigger_retrain({"epochs": 5})
        # … run training …
        pipeline.promote("/models/v2.pt", registry={}, metrics={"accuracy": 0.88})
"""

from __future__ import annotations

from .eval_gate import EvalGate, EvalGateResult
from .pipeline import ContinuousLearningPipeline, RetrainingJob
from .trigger import RetrainingTrigger

__all__ = [
    "ContinuousLearningPipeline",
    "EvalGate",
    "EvalGateResult",
    "RetrainingJob",
    "RetrainingTrigger",
]
