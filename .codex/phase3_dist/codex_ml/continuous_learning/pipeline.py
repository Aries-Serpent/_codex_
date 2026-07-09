"""Continuous learning pipeline — orchestrates drift detection, retraining
triggers, and model promotion.

The ``ContinuousLearningPipeline`` ties together the data/model drift monitors
(``DataDriftDetector``, ``ModelDriftDetector``) with the ``EvalGate`` and
``RetrainingTrigger`` dataclass to form an end-to-end retraining loop.

Architecture overview
---------------------
::

    drift_result
        │
        ▼
    should_retrain()  ──── False ──► done
        │ True
        ▼
    trigger_retrain()  ─► RetrainingJob (descriptor)
        │
        ▼  (after training completes externally)
    eval_gate()  ──── False ──► reject new model
        │ True
        ▼
    promote()  ──► model registered in registry

Usage example::

    from codex_ml.continuous_learning import ContinuousLearningPipeline

    pipeline = ContinuousLearningPipeline(
        drift_threshold=0.2,
        eval_gate_min_accuracy=0.80,
        eval_gate_max_loss=0.5,
        eval_gate_min_improvement_pct=1.0,
    )

    # --- drift detection (done by DataDriftDetector / ModelDriftDetector) ---
    drift_info = {"score": 0.35, "method": "psi", "drifted": True}

    if pipeline.should_retrain(drift_info):
        job = pipeline.trigger_retrain({"epochs": 5, "lr": 1e-4})
        # ... run training externally, collect metrics ...
        metrics = {"accuracy": 0.87, "loss": 0.38, "baseline_accuracy": 0.83}
        if pipeline.eval_gate(metrics):
            pipeline.promote("/models/new_model.pt", registry={})
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .eval_gate import EvalGate
from .trigger import RetrainingTrigger

logger = logging.getLogger(__name__)

__all__ = ["ContinuousLearningPipeline", "RetrainingJob"]


# ---------------------------------------------------------------------------
# RetrainingJob — lightweight descriptor returned by trigger_retrain()
# ---------------------------------------------------------------------------


@dataclass
class RetrainingJob:
    """Descriptor for a retraining job created by the pipeline.

    Attributes:
        job_id: Unique identifier (ISO timestamp by default).
        trigger: The :class:`RetrainingTrigger` that caused this job.
        config: Training configuration snapshot.
        status: Job status string (``"pending"``, ``"running"``, ``"done"``,
            ``"failed"``).
    """

    job_id: str
    trigger: RetrainingTrigger
    config: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dictionary."""
        return {
            "job_id": self.job_id,
            "trigger": self.trigger.to_dict(),
            "config": dict(self.config),
            "status": self.status,
        }


# ---------------------------------------------------------------------------
# ContinuousLearningPipeline
# ---------------------------------------------------------------------------


class ContinuousLearningPipeline:
    """Orchestrates drift-triggered retraining and model promotion.

    Parameters
    ----------
    drift_threshold:
        Drift score above which retraining is triggered.  Applied to any
        drift result that provides a ``"score"`` key (or ``score`` attribute).
    eval_gate_min_accuracy:
        Forwarded to :class:`EvalGate` as ``min_accuracy``.
    eval_gate_max_loss:
        Forwarded to :class:`EvalGate` as ``max_loss``.
    eval_gate_min_improvement_pct:
        Forwarded to :class:`EvalGate` as ``min_improvement_pct``.
    """

    def __init__(
        self,
        *,
        drift_threshold: float = 0.2,
        eval_gate_min_accuracy: float | None = None,
        eval_gate_max_loss: float | None = None,
        eval_gate_min_improvement_pct: float | None = None,
    ) -> None:
        self.drift_threshold = drift_threshold
        self._gate = EvalGate(
            min_accuracy=eval_gate_min_accuracy,
            max_loss=eval_gate_max_loss,
            min_improvement_pct=eval_gate_min_improvement_pct,
        )
        self._last_trigger: RetrainingTrigger | None = None
        self._last_job: RetrainingJob | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def should_retrain(self, drift_result: Any) -> bool:
        """Return ``True`` if *drift_result* indicates retraining is needed.

        Parameters
        ----------
        drift_result:
            Either a mapping (dict) or an object with a ``score`` attribute
            and optionally a ``drifted`` attribute.  The pipeline retriggers
            retraining when ``score > drift_threshold`` **or** when
            ``drifted is True`` (if the attribute exists).

        Returns
        -------
        bool
        """
        score, drifted = self._extract_drift_info(drift_result)

        if drifted is True:
            logger.info("should_retrain: drift flag set — triggering (score=%.4f)", score)
            return True

        if score is not None and score > self.drift_threshold:
            logger.info(
                "should_retrain: score %.4f > threshold %.4f — triggering",
                score,
                self.drift_threshold,
            )
            return True

        logger.debug(
            "should_retrain: no retraining needed (score=%s, drifted=%s)",
            score,
            drifted,
        )
        return False

    def trigger_retrain(self, config: dict[str, Any] | None = None) -> RetrainingJob:
        """Create and return a :class:`RetrainingJob` descriptor.

        Parameters
        ----------
        config:
            Arbitrary training configuration snapshot stored in the trigger
            and job.

        Returns
        -------
        RetrainingJob
        """
        cfg = dict(config or {})
        trigger = RetrainingTrigger(
            reason="drift_threshold_exceeded",
            drift_score=self.drift_threshold,
            timestamp=datetime.now(UTC),
            config_snapshot=cfg,
        )
        job_id = f"retrain_{trigger.timestamp.strftime('%Y%m%dT%H%M%S')}"
        job = RetrainingJob(job_id=job_id, trigger=trigger, config=cfg)
        self._last_trigger = trigger
        self._last_job = job
        logger.info("trigger_retrain: created job %s", job_id)
        return job

    def eval_gate(self, metrics: dict[str, Any]) -> bool:
        """Validate new model metrics against the configured eval gate.

        Parameters
        ----------
        metrics:
            Evaluation metrics dict.  See :meth:`EvalGate.evaluate` for
            recognised keys.

        Returns
        -------
        bool
            ``True`` if the model passes all thresholds; ``False`` otherwise.
        """
        result = self._gate.evaluate(metrics)
        if not result.passed:
            logger.warning("eval_gate: model REJECTED — failures: %s", result.reasons)
        return result.passed

    def promote(
        self,
        model_path: str,
        registry: dict[str, Any],
        metrics: dict[str, Any] | None = None,
    ) -> bool:
        """Promote *model_path* to the registry if the eval gate passes.

        If *metrics* is provided the eval gate is re-evaluated before
        promotion.  If *metrics* is ``None`` the caller is assumed to have
        already called :meth:`eval_gate` and the model is promoted
        unconditionally (they take responsibility for the gate check).

        Parameters
        ----------
        model_path:
            Path to the new model artefact.
        registry:
            Mutable registry dict that is updated in-place with the new model
            path under the key ``"model_path"``.
        metrics:
            Optional metrics dict.  When supplied the eval gate is enforced.

        Returns
        -------
        bool
            ``True`` if the model was promoted; ``False`` if the eval gate
            rejected it.
        """
        if metrics is not None:
            if not self.eval_gate(metrics):
                logger.warning("promote: promotion BLOCKED by eval gate")
                return False

        registry["model_path"] = model_path
        registry["promoted_at"] = datetime.now(UTC).isoformat()
        if self._last_job is not None:
            registry["job_id"] = self._last_job.job_id
            self._last_job.status = "done"

        logger.info("promote: model promoted → %s", model_path)
        return True

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def last_trigger(self) -> RetrainingTrigger | None:
        """The most recent :class:`RetrainingTrigger`, or ``None``."""
        return self._last_trigger

    @property
    def last_job(self) -> RetrainingJob | None:
        """The most recent :class:`RetrainingJob`, or ``None``."""
        return self._last_job

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_drift_info(
        drift_result: Any,
    ) -> tuple[float | None, bool | None]:
        """Extract (score, drifted) from a drift result object or dict."""
        if isinstance(drift_result, dict):
            score = drift_result.get("score") or drift_result.get("drift_score")
            drifted = drift_result.get("drifted")
            return (float(score) if score is not None else None, drifted)

        # Object with attributes (e.g. DriftResult dataclass)
        score = getattr(drift_result, "score", None) or getattr(drift_result, "drift_score", None)
        drifted = getattr(drift_result, "drifted", None)
        return (float(score) if score is not None else None, drifted)
