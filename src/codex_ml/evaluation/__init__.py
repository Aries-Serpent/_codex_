"""Evaluation APIs with optional, collision-free standalone contracts.

``EvaluationRunner`` remains the legacy orchestration class because it is not
substitutable with the standalone scalar runner. Constructing the legacy class
emits a one-time deprecation warning; it is scheduled for removal in
``codex-ml 0.5.0``.
"""

from __future__ import annotations

__all__ = [
    "Criterion",
    "EvalResult",
    "EvaluationBatch",
    "EvaluationConfig",
    "EvaluationReport",
    "EvaluationResult",
    "EvaluationRunner",
    "Logger",
    "ScalarEvaluationRunner",
    "_safe_item",
    "evaluate_epoch",
    "run_evaluation",
]

from .loop import Criterion, EvalResult, Logger, _safe_item, evaluate_epoch  # noqa: E402
from .runner import EvaluationConfig, EvaluationRunner  # noqa: E402

try:
    from codex_evaluation import (
        EvaluationBatch,
        EvaluationReport,
    )
    from codex_evaluation import (
        EvaluationRunner as ScalarEvaluationRunner,
    )
except ImportError:  # pragma: no cover - standalone distribution is optional
    EvaluationBatch = None  # type: ignore[assignment,misc]
    EvaluationReport = None  # type: ignore[assignment,misc]
    ScalarEvaluationRunner = None  # type: ignore[assignment,misc]

# Provide aliases for backward compatibility
EvaluationResult = EvalResult
run_evaluation = evaluate_epoch
