"""Evaluation gate that validates a newly trained model before promotion.

The ``EvalGate`` checks that a new model's evaluation metrics meet or exceed
a configurable quality bar before it is allowed to replace the current
production model.

Usage example::

    from codex_ml.continuous_learning.eval_gate import EvalGate

    gate = EvalGate(min_accuracy=0.80, max_loss=0.5, min_improvement_pct=1.0)

    metrics = {"accuracy": 0.85, "loss": 0.42, "baseline_accuracy": 0.83}
    passed, reasons = gate.evaluate(metrics)
    if passed:
        logger.info("Model passed eval gate — safe to promote.")
    else:
        logger.info("Eval gate FAILED:", reasons)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from codex.logging.structured_logger import logger

logger = logging.getLogger(__name__)

__all__ = ["EvalGate", "EvalGateResult"]


@dataclass
class EvalGateResult:
    """Result returned by :meth:`EvalGate.evaluate`.

    Attributes:
        passed: ``True`` if ALL configured thresholds were met.
        reasons: List of human-readable failure reasons (empty if passed).
        metrics: The metrics dict that was evaluated (shallow copy).
    """

    passed: bool
    reasons: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dictionary."""
        return {
            "passed": self.passed,
            "reasons": list(self.reasons),
            "metrics": dict(self.metrics),
        }


class EvalGate:
    """Configurable evaluation gate for model promotion decisions.

    Parameters
    ----------
    min_accuracy:
        Minimum accuracy the new model must achieve (``0.0``–``1.0``).
        Set to ``None`` to skip this check.
    max_loss:
        Maximum loss the new model may have.  Set to ``None`` to skip.
    min_improvement_pct:
        Minimum percentage improvement over baseline accuracy required.
        E.g. ``1.0`` means the new model must be at least 1 % better than the
        baseline.  Requires ``"baseline_accuracy"`` to be present in the
        metrics dict.  Set to ``None`` to skip.
    """

    def __init__(
        self,
        *,
        min_accuracy: float | None = None,
        max_loss: float | None = None,
        min_improvement_pct: float | None = None,
    ) -> None:
        self.min_accuracy = min_accuracy
        self.max_loss = max_loss
        self.min_improvement_pct = min_improvement_pct

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(self, metrics: dict[str, Any]) -> EvalGateResult:
        """Check *metrics* against all configured thresholds.

        Parameters
        ----------
        metrics:
            Dictionary of evaluation metrics.  Recognised keys:

            * ``"accuracy"`` — float in ``[0, 1]``
            * ``"loss"`` — non-negative float
            * ``"baseline_accuracy"`` — float in ``[0, 1]`` (required when
              *min_improvement_pct* is configured)

        Returns
        -------
        EvalGateResult
            Contains ``passed`` flag and list of failure ``reasons``.
        """
        failures: list[str] = []

        accuracy = metrics.get("accuracy")
        loss = metrics.get("loss")
        baseline_accuracy = metrics.get("baseline_accuracy")

        # ---- min_accuracy check ----------------------------------------
        if self.min_accuracy is not None:
            if accuracy is None:
                failures.append(
                    f"min_accuracy={self.min_accuracy}: 'accuracy' key missing from metrics"
                )
            elif accuracy < self.min_accuracy:
                failures.append(f"min_accuracy={self.min_accuracy}: got accuracy={accuracy:.4f}")

        # ---- max_loss check --------------------------------------------
        if self.max_loss is not None:
            if loss is None:
                failures.append(f"max_loss={self.max_loss}: 'loss' key missing from metrics")
            elif loss > self.max_loss:
                failures.append(f"max_loss={self.max_loss}: got loss={loss:.4f}")

        # ---- min_improvement_pct check ---------------------------------
        if self.min_improvement_pct is not None:
            if accuracy is None:
                failures.append("min_improvement_pct check: 'accuracy' key missing from metrics")
            elif baseline_accuracy is None:
                failures.append(
                    "min_improvement_pct check: 'baseline_accuracy' key missing from metrics"
                )
            else:
                if baseline_accuracy <= 0.0:
                    failures.append("min_improvement_pct check: baseline_accuracy must be > 0")
                else:
                    improvement = (accuracy - baseline_accuracy) / baseline_accuracy * 100.0
                    if improvement < self.min_improvement_pct:
                        failures.append(
                            f"min_improvement_pct={self.min_improvement_pct}%: "
                            f"got {improvement:.2f}% improvement"
                        )

        passed = len(failures) == 0
        if passed:
            logger.info("EvalGate: PASSED — all thresholds met")
        else:
            logger.warning("EvalGate: FAILED — %d check(s) failed: %s", len(failures), failures)

        return EvalGateResult(passed=passed, reasons=failures, metrics=dict(metrics))

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"EvalGate(min_accuracy={self.min_accuracy}, "
            f"max_loss={self.max_loss}, "
            f"min_improvement_pct={self.min_improvement_pct})"
        )
