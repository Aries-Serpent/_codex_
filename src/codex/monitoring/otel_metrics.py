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

# Register both instruments in the global in-memory registry so they are
# accessible by name from anywhere (e.g. health-check endpoints).
metrics.register(workflow_duration)
metrics.register(workflow_step_duration)

__all__ = [
    "workflow_duration",
    "workflow_step_duration",
]
