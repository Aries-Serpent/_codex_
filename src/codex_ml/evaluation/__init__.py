"""Evaluation module for codex_ml.

Provides robust evaluation loops with metrics logging and checkpoint integration.
"""

from __future__ import annotations

__all__ = [
    "Criterion",
    "EvalResult",
    "EvaluationConfig",
    "EvaluationResult",
    "EvaluationRunner",
    "Logger",
    "_safe_item",
    "evaluate_epoch",
    "run_evaluation",
]

from .loop import Criterion, EvalResult, Logger, _safe_item, evaluate_epoch
from .runner import EvaluationConfig, EvaluationRunner

# Provide aliases for backward compatibility
EvaluationResult = EvalResult
run_evaluation = evaluate_epoch
