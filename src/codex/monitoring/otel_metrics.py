"""Compatibility wrapper for ``codex.monitoring.otel_metrics``."""

from __future__ import annotations

from aries_serpent_core.monitoring.otel_metrics import (  # noqa: F401
    compute_coherence,
    workflow_coherence_score,
    workflow_duration,
    workflow_step_duration,
)

__all__ = [
    "compute_coherence",
    "workflow_coherence_score",
    "workflow_duration",
    "workflow_step_duration",
]
