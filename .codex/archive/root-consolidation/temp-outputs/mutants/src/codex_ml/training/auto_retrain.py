"""Automated Model Retraining Pipeline (Gap 38).

Wires :class:`~codex_ml.monitoring.model_drift.ModelDriftDetector` output into
a retrain-trigger decision and config-preparation layer.  The pipeline is
designed to be called from ``model-drift-retrain.yml`` via a
``repository_dispatch`` event (type ``drift-detected``) or directly from Python.

Workflow integration
--------------------
The GitHub Actions workflow ``model-drift-retrain.yml`` fires the retrain job
when ``detect-drift`` outputs ``should_retrain=true``.  You can also trigger it
programmatically by dispatching a ``repository_dispatch`` event::

    gh api repos/{owner}/{repo}/dispatches \\
        --method POST \\
        -F event_type=drift-detected \\
        -F client_payload[drift_score]=0.25 \\
        -F client_payload[samples_count]=5000 \\
        -F client_payload[model_id]=codex-primary \\
        -F client_payload[triggered_by]=auto_retrain_pipeline

The ``client_payload`` schema is documented below in
:data:`DISPATCH_PAYLOAD_SCHEMA`.

Classes
-------
- :class:`RetrainResult`      — immutable result record for a pipeline run
- :class:`AutoRetrainPipeline` — decision + config-prep + orchestration
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "AutoRetrainPipeline",
    "DISPATCH_PAYLOAD_SCHEMA",
    "RetrainResult",
]

# ---------------------------------------------------------------------------
# repository_dispatch payload schema documentation
# ---------------------------------------------------------------------------

#: JSON schema that describes the ``client_payload`` expected by
#: ``model-drift-retrain.yml`` when an external caller fires the
#: ``drift-detected`` repository_dispatch event.
#:
#: Example payload (JSON)::
#:
#:     {
#:       "drift_score": 0.25,
#:       "samples_count": 5000,
#:       "model_id": "codex-primary",
#:       "triggered_by": "auto_retrain_pipeline",
#:       "js_divergence": 0.08,
#:       "reasons": ["JSD=0.08 exceeds threshold=0.05"]
#:     }
DISPATCH_PAYLOAD_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "drift-detected repository_dispatch client_payload",
    "properties": {
        "drift_score": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": (
                "Aggregate drift score in [0, 1].  Mapped from "
                "DriftResult.js_divergence when available, otherwise 1.0 if "
                "drift_detected is True and 0.0 otherwise."
            ),
        },
        "samples_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of new samples available for retraining.",
        },
        "model_id": {
            "type": "string",
            "description": "Identifier of the model that triggered drift.",
        },
        "triggered_by": {
            "type": "string",
            "description": "Human-readable source that fired this event.",
        },
        "js_divergence": {
            "type": ["number", "null"],
            "description": "Raw Jensen-Shannon divergence value from DriftResult.",
        },
        "reasons": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Human-readable drift reasons from DriftResult.reasons.",
        },
    },
    "required": ["drift_score"],
    "additionalProperties": True,
}


# ---------------------------------------------------------------------------
# RetrainResult
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RetrainResult:
    """Immutable record produced by :meth:`AutoRetrainPipeline.run`.

    Attributes
    ----------
    triggered:
        ``True`` when retraining was triggered (drift above threshold).
    reason:
        Human-readable explanation for the decision.
    config_snapshot:
        Copy of the retrain config dict prepared during the run, or an empty
        dict when ``triggered`` is ``False``.
    timestamp:
        UTC ISO-8601 timestamp of when the result was created, e.g.
        ``"2025-01-15T02:30:00+00:00"``.
    """

    triggered: bool
    reason: str
    config_snapshot: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {
            "triggered": self.triggered,
            "reason": self.reason,
            "config_snapshot": self.config_snapshot,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# AutoRetrainPipeline
# ---------------------------------------------------------------------------


class AutoRetrainPipeline:
    """Decision layer and config builder for automated model retraining.

    This class consumes the output of
    :class:`~codex_ml.monitoring.model_drift.ModelDriftDetector` and decides
    whether retraining should be triggered.  When triggered it prepares a
    retrain configuration dict that is forwarded to the training engine or
    emitted as a GitHub Actions ``repository_dispatch`` payload.

    Parameters
    ----------
    drift_threshold:
        Minimum ``js_divergence`` (or proxy score) that must be exceeded for
        retraining to trigger.  Defaults to ``0.05`` (same default used in the
        GHA workflow via ``MODEL_DRIFT_THRESHOLD``).
    min_samples:
        Minimum number of new samples that must be available before retraining
        is allowed.  Set to ``0`` (default) to disable this guard.
    model_id:
        Identifier used in the prepared config and dispatch payload to
        reference which model is being retrained.
    extra_config:
        Optional base configuration additions merged into every prepared
        config dict.

    Examples
    --------
    >>> from codex_ml.monitoring.model_drift import ModelDriftDetector
    >>> detector = ModelDriftDetector(js_threshold=0.05)
    >>> detector.update_baseline([0.2, 0.5, 0.3])
    >>> drift = detector.check([0.1, 0.3, 0.6])
    >>> pipeline = AutoRetrainPipeline(drift_threshold=0.05)
    >>> result = pipeline.run(drift, base_config={"epochs": 3})
    >>> result.triggered
    True
    """

    def __init__(
        self,
        drift_threshold: float = 0.05,
        min_samples: int = 0,
        model_id: str = "codex-primary",
        extra_config: dict[str, Any] | None = None,
    ) -> None:
        if not (0.0 < drift_threshold <= 1.0):
            raise ValueError(f"drift_threshold must be in (0, 1], got {drift_threshold}")
        if min_samples < 0:
            raise ValueError(f"min_samples must be >= 0, got {min_samples}")
        self.drift_threshold = drift_threshold
        self.min_samples = min_samples
        self.model_id = model_id
        self.extra_config: dict[str, Any] = extra_config or {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def should_retrain(self, drift_result: Any, samples_available: int = 0) -> bool:
        """Decide whether retraining should be triggered.

        Parameters
        ----------
        drift_result:
            A :class:`~codex_ml.monitoring.model_drift.DriftResult` instance
            (or any object with a ``drift_detected: bool`` attribute and an
            optional ``js_divergence: float | None`` attribute).
        samples_available:
            Number of new samples ready for training.  Checked against
            :attr:`min_samples` when ``> 0``.

        Returns
        -------
        bool
            ``True`` when all of the following conditions hold:

            1. ``drift_result.drift_detected`` is ``True``.
            2. ``drift_result.js_divergence`` (if set) exceeds
               :attr:`drift_threshold`, **or** ``js_divergence`` is ``None``
               (meaning another metric triggered drift without a JSD value).
            3. ``samples_available >= min_samples`` (unless ``min_samples``
               is 0, in which case this guard is skipped).
        """
        if not getattr(drift_result, "drift_detected", False):
            return False

        js_div: float | None = getattr(drift_result, "js_divergence", None)
        if js_div is not None and js_div <= self.drift_threshold:
            # Drift flag set but JS divergence is below our pipeline threshold —
            # another metric (confidence) may have flagged it; still allow
            # triggering so we do not mask legitimate confidence degradation.
            # However, we respect the threshold strictly for JSD-only cases:
            # if reasons list only contains a JSD reason and it's ≤ threshold,
            # don't trigger.
            reasons: list[str] = getattr(drift_result, "reasons", [])
            jsd_only = all("JSD" in r or "divergence" in r.lower() for r in reasons)
            if jsd_only and js_div <= self.drift_threshold:
                logger.debug(
                    "Drift flag set but JSD=%.4f ≤ threshold=%.4f — skipping.",
                    js_div,
                    self.drift_threshold,
                )
                return False

        if self.min_samples > 0 and samples_available < self.min_samples:
            logger.debug(
                "Drift detected but only %d samples available (min=%d) — skipping.",
                samples_available,
                self.min_samples,
            )
            return False

        return True

    def prepare_retrain_config(
        self,
        base_config: dict[str, Any],
        drift_result: Any,
        samples_available: int = 0,
    ) -> dict[str, Any]:
        """Build a retrain configuration dict from a base config and drift info.

        The returned dict is safe to pass to a training engine or serialise
        as the ``client_payload`` of a ``repository_dispatch`` event.

        Parameters
        ----------
        base_config:
            Caller-supplied base configuration (e.g. ``{"epochs": 3,
            "learning_rate": 1e-4}``).  This dict is **not** mutated.
        drift_result:
            A :class:`~codex_ml.monitoring.model_drift.DriftResult` instance.
        samples_available:
            Number of new samples available (forwarded to the payload).

        Returns
        -------
        dict[str, Any]
            Merged config containing at minimum:

            * All keys from ``base_config``
            * All keys from :attr:`extra_config`
            * ``drift_score`` — JS divergence or 1.0 if ``drift_detected``
            * ``model_id`` — from :attr:`model_id`
            * ``triggered_by`` — ``"auto_retrain_pipeline"``
            * ``js_divergence`` — raw value from drift_result
            * ``reasons`` — list of drift reasons
            * ``samples_count`` — ``samples_available``
            * ``retrain_timestamp`` — UTC ISO-8601 timestamp
        """
        js_div: float | None = getattr(drift_result, "js_divergence", None)
        drift_detected: bool = getattr(drift_result, "drift_detected", False)

        # Derive a scalar drift score for the workflow
        if js_div is not None:
            drift_score = js_div
        elif drift_detected:
            drift_score = 1.0
        else:
            drift_score = 0.0

        config: dict[str, Any] = {}
        config.update(self.extra_config)
        config.update(base_config)
        config.update(
            {
                "drift_score": drift_score,
                "model_id": self.model_id,
                "triggered_by": "auto_retrain_pipeline",
                "js_divergence": js_div,
                "reasons": list(getattr(drift_result, "reasons", [])),
                "samples_count": samples_available,
                "retrain_timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return config

    def run(
        self,
        drift_result: Any,
        base_config: dict[str, Any] | None = None,
        samples_available: int = 0,
    ) -> RetrainResult:
        """Run the full pipeline: check drift → prepare config → return result.

        Parameters
        ----------
        drift_result:
            A :class:`~codex_ml.monitoring.model_drift.DriftResult` instance.
        base_config:
            Base training config dict.  Defaults to ``{}``.
        samples_available:
            Number of new samples ready for training.

        Returns
        -------
        RetrainResult
            ``triggered=True`` when drift exceeds the threshold; ``False``
            otherwise.  When triggered, :attr:`~RetrainResult.config_snapshot`
            contains the prepared config.
        """
        base_config = base_config or {}
        triggered = self.should_retrain(drift_result, samples_available)

        if triggered:
            config_snapshot = self.prepare_retrain_config(
                base_config, drift_result, samples_available
            )
            reasons: list[str] = getattr(drift_result, "reasons", [])
            reason_str = "; ".join(reasons) if reasons else "drift_detected=True"
            logger.info(
                "AutoRetrainPipeline: retrain triggered for model=%s — %s",
                self.model_id,
                reason_str,
            )
            return RetrainResult(
                triggered=True,
                reason=reason_str,
                config_snapshot=config_snapshot,
            )

        logger.debug(
            "AutoRetrainPipeline: no retrain needed for model=%s",
            self.model_id,
        )
        return RetrainResult(
            triggered=False,
            reason="drift below threshold or not detected",
            config_snapshot={},
        )
