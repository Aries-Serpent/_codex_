"""Evaluation module for codex_ml.

Provides robust evaluation loops with metrics logging and checkpoint integration.
"""
from __future__ import annotations

__all__ = ["evaluate_epoch", "EvalResult", "Criterion", "Logger", "_safe_item"]

from .loop import Criterion, EvalResult, Logger, evaluate_epoch, _safe_item
