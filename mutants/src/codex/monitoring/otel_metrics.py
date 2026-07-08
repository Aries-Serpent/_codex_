"""OpenTelemetry-style workflow timing metrics.

This module pre-registers the standard workflow timing histogram used across
all GitHub Actions jobs so that any code that imports this module can record
durations with a single call:

    from codex.monitoring.otel_metrics import workflow_duration

    workflow_duration.observe(elapsed_seconds)

The histogram is backed by the lightweight in-memory ``_MetricRegistry``
defined in ``codex.monitoring``.  It intentionally does *not* pull in the
full OpenTelemetry SDK (which is an optional heavy dependency) but follows
the same naming conventions so that a future migration to the OTEL SDK can
be done by swapping this module without touching call sites.

Histogram name follows OTEL semantic-conventions:
    ``workflow.job.duration`` (seconds, gauge-histogram)

Coherence score histogram:
    ``workflow.coherence.score`` (dimensionless 0.0–1.0)

The coherence score measures semantic alignment between workflow step
outcomes and expected CI policy constraints.  A score of 1.0 means all
steps completed exactly as policy dictates; 0.0 means complete divergence.

Usage (coherence)::

    from codex.monitoring.otel_metrics import workflow_coherence_score

    # Compute per-run coherence and observe once per workflow run
    score = compute_run_coherence(actual_steps, expected_steps)
    workflow_coherence_score.observe(score)
"""

from __future__ import annotations

from codex.monitoring import Histogram, metrics

# ── Pre-registered instruments ────────────────────────────────────────────────

#: Records the wall-clock duration (in seconds) of a CI workflow job.
#: Emit one observation per job at job completion::
#:
#:     import time
#:     t0 = time.monotonic()
#:     ...
#:     workflow_duration.observe(time.monotonic() - t0)
workflow_duration: Histogram = Histogram(
    name="workflow.job.duration",
    description="Wall-clock duration of a CI workflow job in seconds.",
    unit="s",
)

#: Records individual step latencies within a workflow job (seconds).
workflow_step_duration: Histogram = Histogram(
    name="workflow.step.duration",
    description="Wall-clock duration of a single workflow step in seconds.",
    unit="s",
)

#: Records workflow run coherence scores (dimensionless, 0.0–1.0).
#:
#: Coherence is the fraction of CI steps whose outcome matches the
#: policy-expected outcome.  Observe once per workflow run after all
#: steps have completed::
#:
#:     actual   = {"lint": "success", "test": "success", "build": "failure"}
#:     expected = {"lint": "success", "test": "success", "build": "success"}
#:     score = compute_coherence(actual, expected)
#:     workflow_coherence_score.observe(score)
#:
#: A histogram (rather than a gauge) is used so that percentile trends
#: (p50/p95 coherence over the last N runs) are available for dashboards.
workflow_coherence_score: Histogram = Histogram(
    name="workflow.coherence.score",
    description=(
        "Fraction of CI workflow steps whose outcome matches the "
        "policy-expected outcome (0.0 = no match, 1.0 = full match)."
    ),
    unit="1",
)

# Register all instruments in the global in-memory registry so they are
# accessible by name from anywhere (e.g. health-check endpoints).
metrics.register(workflow_duration)
metrics.register(workflow_step_duration)
metrics.register(workflow_coherence_score)


def compute_coherence(
    actual: dict[str, str],
    expected: dict[str, str],
) -> float:
    """Return a coherence score in [0.0, 1.0] for a workflow run.

    The score is the fraction of *expected* steps whose actual outcome
    matches the expected outcome.  Steps present in ``actual`` but absent
    from ``expected`` are ignored (they are not constrained by policy).
    If ``expected`` is empty, returns 1.0 (vacuously coherent).

    Args:
        actual:   Mapping of step-name → observed outcome string
                  (e.g. ``"success"``, ``"failure"``, ``"skipped"``).
        expected: Mapping of step-name → policy-required outcome string.

    Returns:
        Float in [0.0, 1.0].

    Example::

        >>> compute_coherence(
        ...     {"lint": "success", "test": "failure"},
        ...     {"lint": "success", "test": "success"},
        ... )
        0.5
    """
    if not expected:
        return 1.0
    matches = sum(1 for step, exp_outcome in expected.items() if actual.get(step) == exp_outcome)
    return matches / len(expected)


__all__ = [
    "compute_coherence",
    "workflow_coherence_score",
    "workflow_duration",
    "workflow_step_duration",
]
