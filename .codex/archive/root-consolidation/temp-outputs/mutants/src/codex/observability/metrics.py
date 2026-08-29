"""Metrics collection system for the Codex agent ecosystem.

from codex.logging.structured_logger import logger
Phase 12.3 — Agent Observability & Telemetry

``MetricsCollector`` tracks per-agent and ecosystem-wide metrics using an
in-memory circular buffer (configurable window size, default 1 000 executions
per agent).  It builds on the ``codex.monitoring.Histogram`` infrastructure
already established in Phase 11.

Key metrics tracked
-------------------
Per-agent:
    latency_p50_ms, latency_p95_ms, latency_p99_ms — execution latency
    percentiles (milliseconds).
    success_rate  — fraction of executions that succeeded (0.0–1.0).
    error_rate    — fraction of executions that failed (0.0–1.0).
    throughput_per_min — rolling executions per minute.
    total_executions — cumulative execution count.

Ecosystem-wide:
    total_tasks_executed — sum across all agents.
    active_agents        — agents with ≥1 execution in the window.
    failed_agents        — agents with error_rate > 0 in the window.
    routing_accuracy     — fraction of routing decisions marked accurate.

Usage::

    from codex.observability.metrics import MetricsCollector

    collector = MetricsCollector(window_size=500)
    collector.record_agent_execution("orchestrator", duration_ms=1250.0, success=True)
    collector.record_agent_execution("ci-auto-healer", duration_ms=8400.0, success=False)

    metrics = collector.get_agent_metrics("orchestrator")
    logger.info(metrics.latency_p99_ms)

    summary = collector.get_ecosystem_summary()
    logger.info(collector.export_prometheus_format())
"""

from __future__ import annotations

import math
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any

# Build on the existing Histogram infrastructure
try:
    from codex.monitoring import Histogram
    from codex.monitoring import metrics as _global_registry

    _MONITORING_AVAILABLE = True
except Exception:  # pragma: no cover – graceful degradation
    _MONITORING_AVAILABLE = False
    _global_registry = None
    Histogram = None


# ── Data structures ───────────────────────────────────────────────────────────


@dataclass
class _ExecutionRecord:
    """Single execution event stored in the sliding window."""

    timestamp: float  # time.monotonic() at recording time
    wall_time: float  # time.time() at recording time
    duration_ms: float  # wall-clock duration in milliseconds
    success: bool  # True if execution succeeded


@dataclass
class AgentMetrics:
    """Point-in-time snapshot of metrics for a single agent.

    All latency values are in milliseconds.  Rates are fractions in [0.0, 1.0].
    """

    agent_id: str
    total_executions: int = 0
    window_executions: int = 0  # executions within the sliding window
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    latency_min_ms: float = 0.0
    latency_max_ms: float = 0.0
    latency_mean_ms: float = 0.0
    success_rate: float = 0.0  # fraction successful
    error_rate: float = 0.0  # fraction failed
    throughput_per_min: float = 0.0  # executions per minute over last 60 s
    last_seen_at: float = 0.0  # wall time of most recent execution


# ── Percentile helper ─────────────────────────────────────────────────────────


def _percentile(sorted_values: list[float], p: float) -> float:
    """Return the *p*-th percentile (0–100) of *sorted_values* (already sorted).

    Uses the nearest-rank method.  Returns 0.0 for an empty list.
    """
    if not sorted_values:
        return 0.0
    n = len(sorted_values)
    rank = math.ceil(p / 100.0 * n)
    rank = max(1, min(rank, n))
    return sorted_values[rank - 1]


# ── MetricsCollector ──────────────────────────────────────────────────────────


class MetricsCollector:
    """In-memory metrics collector for the Codex agent ecosystem.

    Uses a sliding window (``window_size`` most recent executions per agent)
    to compute latency percentiles, success/error rates, and throughput.

    The collector is fully thread-safe: all public methods acquire an internal
    ``threading.Lock`` before accessing shared state.

    Args:
        window_size:
            Maximum number of execution records to retain per agent.
            Older records are evicted when the window is full (FIFO).
            Default: 1000.
        register_histograms:
            If *True* and ``codex.monitoring`` is available, register
            per-agent Histogram instruments in the global metric registry
            so they can be scraped alongside the existing OTEL histograms.
            Default: *True*.

    Example::

        collector = MetricsCollector()
        collector.record_agent_execution("orchestrator", 350.0, True)
        m = collector.get_agent_metrics("orchestrator")
        assert m.success_rate == 1.0
    """

    def __init__(
        self,
        window_size: int = 1000,
        register_histograms: bool = True,
    ) -> None:
        self._window_size: int = window_size
        self._register_histograms: bool = register_histograms and _MONITORING_AVAILABLE
        self._lock: threading.Lock = threading.Lock()

        # Per-agent execution windows: agent_id → deque[_ExecutionRecord]
        self._windows: dict[str, deque[_ExecutionRecord]] = defaultdict(
            lambda: deque(maxlen=window_size)
        )
        # Per-agent lifetime execution count (never resets with window)
        self._total_counts: dict[str, int] = defaultdict(int)
        # Routing decision tracking: (total, accurate)
        self._routing_total: int = 0
        self._routing_accurate: int = 0
        # Optional Histograms registered in the global registry
        self._histograms: dict[str, Any] = {}

    # ── Recording ─────────────────────────────────────────────────────────────

    def record_agent_execution(
        self,
        agent_id: str,
        duration_ms: float,
        success: bool,
    ) -> None:
        """Record a single agent execution.

        Args:
            agent_id:    Identifier of the executing agent.
            duration_ms: Wall-clock execution time in milliseconds.
            success:     ``True`` if the execution succeeded, ``False`` on
                         failure/error.

        Example::

            collector.record_agent_execution(
                "ci-auto-healer-agent", duration_ms=4200.0, success=True
            )
        """
        now_mono = time.monotonic()
        now_wall = time.time()
        record = _ExecutionRecord(
            timestamp=now_mono,
            wall_time=now_wall,
            duration_ms=float(duration_ms),
            success=bool(success),
        )
        with self._lock:
            self._windows[agent_id].append(record)
            self._total_counts[agent_id] += 1
            # Optionally observe into global Histogram
            if self._register_histograms and _MONITORING_AVAILABLE:
                self._observe_histogram(agent_id, duration_ms / 1000.0)

    def record_routing_decision(self, accurate: bool) -> None:
        """Record whether a routing decision was accurate.

        Args:
            accurate: ``True`` if the chosen agent successfully handled the
                      task, ``False`` if it had to be re-routed or failed.
        """
        with self._lock:
            self._routing_total += 1
            if accurate:
                self._routing_accurate += 1

    # ── Querying ──────────────────────────────────────────────────────────────

    def get_agent_metrics(self, agent_id: str) -> AgentMetrics:
        """Return a point-in-time ``AgentMetrics`` snapshot for *agent_id*.

        If *agent_id* has no recorded executions, returns a zero-valued
        ``AgentMetrics`` with ``total_executions == 0``.

        Args:
            agent_id: The agent to query.

        Returns:
            ``AgentMetrics`` dataclass instance.
        """
        with self._lock:
            window: deque[_ExecutionRecord] = self._windows[agent_id]
            total = self._total_counts[agent_id]
            records = list(window)  # snapshot inside lock to prevent RuntimeError

        n = len(records)
        if n == 0:
            return AgentMetrics(agent_id=agent_id, total_executions=total)

        durations_sorted = sorted(r.duration_ms for r in records)
        successes = sum(1 for r in records if r.success)
        now_mono = time.monotonic()
        recent_60s = [r for r in records if (now_mono - r.timestamp) <= 60.0]

        return AgentMetrics(
            agent_id=agent_id,
            total_executions=total,
            window_executions=n,
            latency_p50_ms=_percentile(durations_sorted, 50.0),
            latency_p95_ms=_percentile(durations_sorted, 95.0),
            latency_p99_ms=_percentile(durations_sorted, 99.0),
            latency_min_ms=durations_sorted[0],
            latency_max_ms=durations_sorted[-1],
            latency_mean_ms=sum(durations_sorted) / n,
            success_rate=successes / n,
            error_rate=(n - successes) / n,
            throughput_per_min=len(recent_60s),
            last_seen_at=max(r.wall_time for r in records),
        )

    def get_ecosystem_summary(self) -> dict[str, Any]:
        """Return an ecosystem-wide metrics summary.

        Returns a ``dict`` containing:

        - ``total_tasks_executed`` (int): Lifetime task count across all agents.
        - ``active_agents`` (int): Number of agents with ≥1 window execution.
        - ``failed_agents`` (int): Number of agents with ``error_rate > 0`` in
          the window.
        - ``routing_accuracy`` (float): Fraction of routing decisions accurate.
        - ``agent_ids`` (list[str]): All known agent identifiers.
        - ``per_agent`` (dict): ``{agent_id: AgentMetrics}`` mapping (as dicts).

        Example::

            summary = collector.get_ecosystem_summary()
            logger.info(f"Active agents: {summary['active_agents']}")
        """
        with self._lock:
            agent_ids = list(self._windows.keys())
            total_routing = self._routing_total
            accurate_routing = self._routing_accurate

        per_agent: dict[str, AgentMetrics] = {aid: self.get_agent_metrics(aid) for aid in agent_ids}
        active = sum(1 for m in per_agent.values() if m.window_executions > 0)
        failed = sum(1 for m in per_agent.values() if m.error_rate > 0.0)
        total_tasks = sum(m.total_executions for m in per_agent.values())
        routing_accuracy = accurate_routing / total_routing if total_routing > 0 else 1.0

        return {
            "total_tasks_executed": total_tasks,
            "active_agents": active,
            "failed_agents": failed,
            "routing_accuracy": routing_accuracy,
            "agent_ids": agent_ids,
            "per_agent": {
                aid: {
                    "total_executions": m.total_executions,
                    "window_executions": m.window_executions,
                    "latency_p50_ms": m.latency_p50_ms,
                    "latency_p95_ms": m.latency_p95_ms,
                    "latency_p99_ms": m.latency_p99_ms,
                    "latency_mean_ms": m.latency_mean_ms,
                    "success_rate": m.success_rate,
                    "error_rate": m.error_rate,
                    "throughput_per_min": m.throughput_per_min,
                }
                for aid, m in per_agent.items()
            },
        }

    # ── Prometheus export ─────────────────────────────────────────────────────

    def export_prometheus_format(self) -> str:
        """Export all metrics as a Prometheus text-format string.

        Generates standard ``# HELP`` / ``# TYPE`` headers followed by metric
        lines.  Does *not* require ``prometheus_client`` — the format is
        generated manually.

        Returns:
            Multi-line string in `Prometheus exposition format
            <https://prometheus.io/docs/instrumenting/exposition_formats/>`_.

        Example::

            logger.info(collector.export_prometheus_format())
        """
        summary = self.get_ecosystem_summary()
        lines: list[str] = []

        def _gauge(
            name: str,
            value: float | int,
            labels: dict[str, str] | None = None,
            help_text: str = "",
            type_hint: str = "gauge",
        ) -> None:
            if help_text:
                lines.append(f"# HELP {name} {help_text}")
            lines.append(f"# TYPE {name} {type_hint}")
            if labels:
                label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
                lines.append(f"{name}{{{label_str}}} {value}")
            else:
                lines.append(f"{name} {value}")

        # ── Ecosystem-level ────────────────────────────────────────────────
        _gauge(
            "codex_agent_total_tasks_executed",
            summary["total_tasks_executed"],
            help_text="Total number of agent task executions across all agents.",
            type_hint="counter",
        )
        _gauge(
            "codex_agent_active_agents",
            summary["active_agents"],
            help_text="Number of agents with at least one execution in the current window.",
        )
        _gauge(
            "codex_agent_failed_agents",
            summary["failed_agents"],
            help_text="Number of agents with error_rate > 0 in the current window.",
        )
        _gauge(
            "codex_routing_accuracy",
            summary["routing_accuracy"],
            help_text="Fraction of routing decisions that correctly matched tasks to agents.",
        )

        # ── Per-agent ──────────────────────────────────────────────────────
        per_agent_metrics = [
            (
                "codex_agent_latency_p50_ms",
                "latency_p50_ms",
                "P50 agent task execution latency in milliseconds.",
            ),
            (
                "codex_agent_latency_p95_ms",
                "latency_p95_ms",
                "P95 agent task execution latency in milliseconds.",
            ),
            (
                "codex_agent_latency_p99_ms",
                "latency_p99_ms",
                "P99 agent task execution latency in milliseconds.",
            ),
            (
                "codex_agent_latency_mean_ms",
                "latency_mean_ms",
                "Mean agent task execution latency in milliseconds.",
            ),
            (
                "codex_agent_success_rate",
                "success_rate",
                "Fraction of executions that succeeded (0.0–1.0).",
            ),
            (
                "codex_agent_error_rate",
                "error_rate",
                "Fraction of executions that failed (0.0–1.0).",
            ),
            (
                "codex_agent_throughput_per_min",
                "throughput_per_min",
                "Agent executions per minute over last 60 s.",
            ),
            (
                "codex_agent_total_executions",
                "total_executions",
                "Lifetime execution count for the agent.",
            ),
        ]

        for metric_name, field_name, help_text in per_agent_metrics:
            lines.append(f"# HELP {metric_name} {help_text}")
            lines.append(f"# TYPE {metric_name} gauge")
            for agent_id, agent_data in summary["per_agent"].items():
                safe_id = agent_id.replace("-", "_").replace(".", "_")
                value = agent_data[field_name]
                lines.append(f'{metric_name}{{agent_id="{safe_id}"}} {value}')

        return "\n".join(lines) + "\n"

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _observe_histogram(self, agent_id: str, duration_s: float) -> None:
        """Register or update a per-agent Histogram in the global registry."""
        hist_name = f"agent.{agent_id}.execution_duration"
        if hist_name not in self._histograms and _MONITORING_AVAILABLE and Histogram is not None:
            hist = Histogram(
                name=hist_name,
                description=f"Execution duration for agent {agent_id!r} in seconds.",
                unit="s",
            )
            try:
                _global_registry.register(hist)
            except Exception:  # pragma: no cover – already registered
                pass
            self._histograms[hist_name] = hist
        hist = self._histograms.get(hist_name)
        if hist is not None:
            try:
                hist.observe(duration_s)
            except Exception:  # pragma: no cover – defensive
                pass


__all__ = ["AgentMetrics", "MetricsCollector"]
