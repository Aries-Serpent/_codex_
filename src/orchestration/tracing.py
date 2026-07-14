"""
Distributed Tracing Framework for Multi-Agent Handoffs (Phase 4D)

Implements comprehensive observability for all agent-to-agent handoffs:
  - Trace ID generation and propagation
  - Structured logging with context
  - Performance metrics collection
  - Error tracking and classification
  - SLA monitoring
  - Visualization-ready output

Usage:
  from src.orchestration.tracing import HandoffTracer, TraceContext
  
  tracer = HandoffTracer()
  with tracer.trace_handoff(
      from_agent="orchestrator-agent",
      to_agent="ci-testing-agent",
      task_id="PR-1234"
  ) as span:
      # Agent handoff work happens here
      span.add_event("agent_started")
      # ... work ...
      span.add_event("agent_completed")
"""

from __future__ import annotations

import json
import logging
import pathlib
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterator, Optional

logger = logging.getLogger(__name__)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TRACES_DIR = REPO_ROOT.parent / ".codex" / "handoff_traces"
TRACES_DIR.mkdir(exist_ok=True, parents=True)
METRICS_DIR = REPO_ROOT.parent / ".codex" / "metrics"
METRICS_DIR.mkdir(exist_ok=True, parents=True)


class SpanStatus(Enum):
    """Trace span status."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"


@dataclass
class TraceEvent:
    """Single event in a trace."""
    name: str
    timestamp: str
    attributes: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TraceSpan:
    """OpenTelemetry-style trace span."""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    
    operation: str  # e.g., "handoff", "execution", "validation"
    from_agent: str
    to_agent: str
    task_id: str
    
    start_time: str
    end_time: Optional[str] = None
    status: SpanStatus = SpanStatus.PENDING
    
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[TraceEvent] = field(default_factory=list)
    
    # Metrics
    duration_ms: Optional[float] = None
    queue_wait_ms: Optional[float] = None
    execution_ms: Optional[float] = None
    
    # SLA tracking
    sla_target_ms: float = 500.0
    sla_compliant: bool = False
    
    # Error tracking
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dict, handling enums and timestamps."""
        data = asdict(self)
        data['status'] = self.status.value
        data['events'] = [e.to_dict() for e in self.events]
        return data
    
    def add_event(self, name: str, **attributes: Any) -> None:
        """Add an event to the span."""
        event = TraceEvent(
            name=name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            attributes=attributes
        )
        self.events.append(event)
    
    def mark_success(self) -> None:
        """Mark span as successful."""
        self.status = SpanStatus.SUCCESS
        self.end_time = datetime.now(timezone.utc).isoformat()
        self._compute_metrics()
        self.sla_compliant = (self.duration_ms or 0) <= self.sla_target_ms
    
    def mark_failed(self, error_code: str, error_message: str) -> None:
        """Mark span as failed."""
        self.status = SpanStatus.FAILED
        self.error_code = error_code
        self.error_message = error_message
        self.end_time = datetime.now(timezone.utc).isoformat()
        self._compute_metrics()
    
    def mark_timeout(self) -> None:
        """Mark span as timed out."""
        self.status = SpanStatus.TIMEOUT
        self.end_time = datetime.now(timezone.utc).isoformat()
        self._compute_metrics()
        self.sla_compliant = False
    
    def _compute_metrics(self) -> None:
        """Compute duration metrics."""
        if self.start_time and self.end_time:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            self.duration_ms = (end - start).total_seconds() * 1000


class TraceContext:
    """Context manager for propagating trace information."""
    
    _current_trace_id: Optional[str] = None
    _current_span_id: Optional[str] = None
    
    @classmethod
    def set_trace_id(cls, trace_id: str) -> None:
        cls._current_trace_id = trace_id
    
    @classmethod
    def get_trace_id(cls) -> str:
        if cls._current_trace_id is None:
            cls._current_trace_id = str(uuid.uuid4())
        return cls._current_trace_id
    
    @classmethod
    def set_span_id(cls, span_id: str) -> None:
        cls._current_span_id = span_id
    
    @classmethod
    def get_span_id(cls) -> Optional[str]:
        return cls._current_span_id
    
    @classmethod
    def new_trace(cls) -> str:
        """Start a new trace."""
        cls._current_trace_id = str(uuid.uuid4())
        cls._current_span_id = None
        return cls._current_trace_id


class HandoffTracer:
    """Tracer for agent handoff operations."""
    
    def __init__(self):
        self._spans: dict[str, TraceSpan] = {}
        self._trace_samples: list[dict[str, Any]] = []
    
    @contextmanager
    def trace_handoff(
        self,
        from_agent: str,
        to_agent: str,
        task_id: str,
        sla_target_ms: float = 500.0,
        operation: str = "handoff",
    ) -> Iterator[TraceSpan]:
        """
        Context manager for tracing a handoff operation.
        
        Example:
            with tracer.trace_handoff("orchestrator", "ci-testing", "PR-123") as span:
                span.add_event("validation_started")
                # ... do work ...
                span.add_event("validation_complete")
        """
        trace_id = TraceContext.get_trace_id()
        span_id = str(uuid.uuid4())
        parent_span_id = TraceContext.get_span_id()
        
        span = TraceSpan(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation=operation,
            from_agent=from_agent,
            to_agent=to_agent,
            task_id=task_id,
            start_time=datetime.now(timezone.utc).isoformat(),
            sla_target_ms=sla_target_ms,
        )
        
        TraceContext.set_span_id(span_id)
        self._spans[span_id] = span
        
        try:
            yield span
            span.mark_success()
        except TimeoutError:
            span.mark_timeout()
            logger.error(f"Handoff timeout: {from_agent} → {to_agent}")
            raise
        except Exception as e:
            error_code = type(e).__name__
            error_message = str(e)
            span.mark_failed(error_code, error_message)
            logger.error(f"Handoff failed: {error_code}: {error_message}")
            raise
        finally:
            # Reset context
            TraceContext.set_span_id(parent_span_id)
            # Save trace
            self._save_span(span)
    
    def _save_span(self, span: TraceSpan) -> None:
        """Save span to disk."""
        trace_file = TRACES_DIR / f"{span.trace_id}_{span.span_id}.json"
        try:
            trace_file.write_text(
                json.dumps(span.to_dict(), indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"Failed to save span: {e}")
    
    def get_trace(self, trace_id: str) -> dict[str, Any]:
        """Retrieve all spans for a trace."""
        spans = [s.to_dict() for s in self._spans.values() if s.trace_id == trace_id]
        return {
            "trace_id": trace_id,
            "span_count": len(spans),
            "spans": spans,
        }
    
    def get_metrics_summary(self) -> dict[str, Any]:
        """Compute metrics across all spans."""
        successful_spans = [
            s for s in self._spans.values()
            if s.status == SpanStatus.SUCCESS
        ]
        
        if not successful_spans:
            return {
                "handoff_success_rate": 0.0,
                "sla_compliance_rate": 0.0,
                "avg_latency_ms": 0.0,
                "p99_latency_ms": 0.0,
            }
        
        durations = [s.duration_ms for s in successful_spans if s.duration_ms]
        sla_compliant = sum(1 for s in successful_spans if s.sla_compliant)
        
        durations.sort()
        p99_idx = max(0, int(len(durations) * 0.99))
        
        return {
            "handoff_success_rate": len(successful_spans) / len(self._spans),
            "sla_compliance_rate": sla_compliant / len(successful_spans),
            "avg_latency_ms": sum(durations) / len(durations),
            "p99_latency_ms": durations[p99_idx] if durations else 0.0,
            "total_handoffs": len(self._spans),
            "successful_handoffs": len(successful_spans),
            "failed_handoffs": sum(1 for s in self._spans.values() if s.status == SpanStatus.FAILED),
            "timeout_handoffs": sum(1 for s in self._spans.values() if s.status == SpanStatus.TIMEOUT),
        }
    
    def export_traces(self, format: str = "json") -> str:
        """Export all traces in specified format."""
        if format == "json":
            data = {
                "traces": [s.to_dict() for s in self._spans.values()],
                "metrics": self.get_metrics_summary(),
                "exported_at": datetime.now(timezone.utc).isoformat(),
            }
            return json.dumps(data, indent=2)
        elif format == "prometheus":
            metrics = self.get_metrics_summary()
            lines = [
                f"# HELP handoff_success_rate Proportion of successful handoffs",
                f"# TYPE handoff_success_rate gauge",
                f"handoff_success_rate {{}} {metrics['handoff_success_rate']}",
                f"",
                f"# HELP handoff_latency_ms Average handoff latency in milliseconds",
                f"# TYPE handoff_latency_ms gauge",
                f"handoff_latency_ms {{}} {metrics['avg_latency_ms']}",
                f"",
                f"# HELP handoff_sla_compliance Proportion of SLA-compliant handoffs",
                f"# TYPE handoff_sla_compliance gauge",
                f"handoff_sla_compliance {{}} {metrics['sla_compliance_rate']}",
            ]
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")


class MetricsCollector:
    """Collect and aggregate handoff metrics."""
    
    def __init__(self):
        self._metrics: list[dict[str, Any]] = []
    
    def record_handoff(
        self,
        from_agent: str,
        to_agent: str,
        latency_ms: float,
        success: bool,
        sla_compliant: bool,
        error_code: Optional[str] = None,
    ) -> None:
        """Record a single handoff metric."""
        metric = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "from_agent": from_agent,
            "to_agent": to_agent,
            "latency_ms": latency_ms,
            "success": success,
            "sla_compliant": sla_compliant,
            "error_code": error_code,
        }
        self._metrics.append(metric)
    
    def percentile_latency(self, percentile: float) -> float:
        """Get latency at specified percentile."""
        if not self._metrics:
            return 0.0
        
        latencies = sorted([m["latency_ms"] for m in self._metrics if m["success"]])
        if not latencies:
            return 0.0
        
        idx = int(len(latencies) * (percentile / 100.0))
        return latencies[min(idx, len(latencies) - 1)]
    
    def agent_load_profile(self, agent_id: str) -> dict[str, Any]:
        """Get load profile for an agent."""
        agent_handoffs = [m for m in self._metrics if m["to_agent"] == agent_id]
        
        if not agent_handoffs:
            return {"agent": agent_id, "handoff_count": 0}
        
        successful = sum(1 for m in agent_handoffs if m["success"])
        sla_compliant = sum(1 for m in agent_handoffs if m["sla_compliant"])
        
        return {
            "agent": agent_id,
            "handoff_count": len(agent_handoffs),
            "success_rate": successful / len(agent_handoffs),
            "sla_compliance": sla_compliant / len(agent_handoffs),
            "avg_latency_ms": sum(m["latency_ms"] for m in agent_handoffs) / len(agent_handoffs),
            "max_latency_ms": max(m["latency_ms"] for m in agent_handoffs),
        }
    
    def export_metrics(self) -> str:
        """Export metrics as JSON."""
        return json.dumps({
            "metric_count": len(self._metrics),
            "metrics": self._metrics,
            "summary": {
                "p50_latency": self.percentile_latency(50),
                "p95_latency": self.percentile_latency(95),
                "p99_latency": self.percentile_latency(99),
            }
        }, indent=2)


if __name__ == "__main__":
    # Demo usage
    tracer = HandoffTracer()
    
    # Example: Trace a handoff
    TraceContext.new_trace()
    try:
        with tracer.trace_handoff("orchestrator", "ci-testing", "PR-1234") as span:
            span.add_event("task_received")
            span.add_event("agent_selected", confidence=0.95)
            time.sleep(0.1)  # Simulate work
            span.add_event("handoff_complete")
    except Exception as e:
        print(f"Handoff failed: {e}")
    
    # Print metrics
    metrics = tracer.get_metrics_summary()
    print("Handoff Metrics:")
    print(json.dumps(metrics, indent=2))
