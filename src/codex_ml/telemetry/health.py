"""Deprecated forwarding module for :mod:`codex_ml_telemetry` health types.

Scheduled for removal in ``codex-ml 0.5.0``.
"""

from __future__ import annotations

try:
    from codex_ml_telemetry import HealthReport, HealthStatus
except ModuleNotFoundError:  # pragma: no cover - optional standalone package
    from codex_ml.monitoring.health import HealthReport, HealthStatus

__all__ = ["HealthReport", "HealthStatus"]
