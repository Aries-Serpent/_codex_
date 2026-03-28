"""Bridge Codex Zendesk metrics into MCP metric collector."""

from __future__ import annotations

from typing import Any

from codex.monitoring import Counter, Histogram, metrics
from codex.zendesk.monitoring.zendesk_metrics import register_zendesk_metrics
from mcp.metrics.mcp_metrics import MetricCollector


def export_zendesk_metrics(collector: MetricCollector) -> list[dict[str, Any]]:
    """Export Zendesk metrics into the MCP collector.

    Args:
        collector: MetricCollector to receive snapshot gauges.

    Returns:
        List of metric snapshots.
    """
    register_zendesk_metrics()
    snapshots: list[dict[str, Any]] = []

    for metric in metrics.registered():
        snapshot = metric.snapshot()
        snapshots.append(snapshot)
        name = snapshot["name"]

        if isinstance(metric, Counter):
            collector.set_gauge(name, float(snapshot.get("value", 0)))
        elif isinstance(metric, Histogram):
            collector.set_gauge(f"{name}_count", float(snapshot.get("count", 0)))
            collector.set_gauge(f"{name}_sum", float(snapshot.get("sum", 0.0)))
            if "avg" in snapshot:
                collector.set_gauge(f"{name}_avg", float(snapshot["avg"]))

    return snapshots


__all__ = ["export_zendesk_metrics"]
