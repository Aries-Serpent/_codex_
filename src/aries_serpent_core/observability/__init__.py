"""Codex Agent Observability & Telemetry package.

from aries_serpent_core.logging.structured_logger import logger
Phase 12.3 — Agent Observability & Telemetry

This package provides structured logging and metrics collection for the Codex
agent ecosystem.  It builds on the existing ``codex.monitoring`` and
``codex.logging`` infrastructure without duplicating any of it.

Quick start::

    from aries_serpent_core.observability import ObservabilityLogger, MetricsCollector

    logger = ObservabilityLogger(session_id="my-session")
    collector = MetricsCollector()

    collector.record_agent_execution("orchestrator", duration_ms=1200, success=True)
    logger.log_agent_action("orchestrator", "route_task", "success", latency_ms=1200)

    summary = collector.get_ecosystem_summary()
    logger.info(summary)
"""

from __future__ import annotations

from aries_serpent_core.observability.logging import ObservabilityLogger
from aries_serpent_core.observability.metrics import AgentMetrics, MetricsCollector

__all__ = [
    "AgentMetrics",
    "MetricsCollector",
    "ObservabilityLogger",
]
