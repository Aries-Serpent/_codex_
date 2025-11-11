"""Evaluation module for codex_ml.

Provides robust evaluation loops with metrics logging and checkpoint integration.
"""
from __future__ import annotations

__all__ = ["run_evaluation", "evaluate_epoch", "EvaluationConfig", "EvaluationResult", "Criterion", "Logger"]

from .loop import Criterion, EvaluationConfig, EvaluationResult, Logger, evaluate_epoch, run_evaluation
