"""Legacy telemetry compatibility facade.

This facade is deprecated and is scheduled for removal in ``codex-ml 0.5.0``.
New code should import from ``codex_ml_telemetry``.
"""

from __future__ import annotations

from codex_ml._compat import warn_deprecated_facade

warn_deprecated_facade(
    "telemetry",
    "codex_ml.telemetry",
    "codex_ml_telemetry",
    removal="0.5.0",
)

try:
    from codex_ml_telemetry import (
        HealthReport,
        HealthStatus,
        MetricsRegistry,
        render_prometheus,
    )
except ImportError:  # pragma: no cover - standalone distribution is optional
    HealthReport = None  # type: ignore[assignment,misc]
    HealthStatus = None  # type: ignore[assignment,misc]
    MetricsRegistry = None  # type: ignore[assignment,misc]
    render_prometheus = None  # type: ignore[assignment]

from .metrics import (  # noqa: E402
    EXAMPLES_PROCESSED,
    REQUEST_LATENCY,
    TRAIN_STEP_DURATION,
    track_time,
)
from .server import start_metrics_server  # noqa: E402

__all__ = [
    "EXAMPLES_PROCESSED",
    "HealthReport",
    "HealthStatus",
    "MetricsRegistry",
    "REQUEST_LATENCY",
    "TRAIN_STEP_DURATION",
    "render_prometheus",
    "start_metrics_server",
    "track_time",
]
