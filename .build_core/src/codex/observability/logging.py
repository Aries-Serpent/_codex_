"""Structured observability logging for the Codex agent ecosystem.

Phase 12.3 — Agent Observability & Telemetry

``ObservabilityLogger`` wraps the existing ``codex.logging.session_logger``
infrastructure and emits structured log records in both JSON and human-readable
text formats.  All public methods are thread-safe.

Structured log schema::

    {
        "timestamp":  "2024-01-15T12:34:56.789Z",  # ISO-8601 UTC
        "session_id": "abc-123",                    # owning session
        "agent_id":   "orchestrator",               # agent identifier
        "action":     "route_task",                 # what was done
        "status":     "success",                    # success | failure | error
        "latency_ms": 1234.5,                       # wall-clock ms (optional)
        "error":      null,                         # error message (optional)
        "metadata":   {}                            # arbitrary key-value pairs
    }

Usage::

    from codex.observability.logging import ObservabilityLogger

    obs = ObservabilityLogger(session_id="run-001", agent_id="orchestrator")
    obs.log_agent_action("orchestrator", "execute_task", "success", latency_ms=750.0)
    obs.log_routing_decision(
        task="generate_code",
        chosen_agent="code-generation-agent",
        confidence=0.92,
        alternatives=["general-purpose", "python-architect-agent"],
    )
"""

from __future__ import annotations

import json
import logging
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

# Integration with existing session_logger (best-effort; degrades gracefully)
try:
    from codex.logging.session_logger import get_session_id as _get_session_id
    from codex.logging.session_logger import log_event as _session_log_event

    _SESSION_LOGGER_AVAILABLE = True
except Exception:  # pragma: no cover – optional integration
    _SESSION_LOGGER_AVAILABLE = False
    _get_session_id = None
    _session_log_event = None


# ── Internal Python logger (standard library) ─────────────────────────────────

_log = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _utcnow_iso() -> str:
    """Return the current UTC time as an ISO-8601 string with 'Z' suffix."""
    utc_now = datetime.now(tz=timezone.utc)
    return utc_now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{utc_now.microsecond // 1000:03d}Z"


def _build_record(
    *,
    session_id: str,
    agent_id: str | None,
    action: str,
    status: str,
    latency_ms: float | None,
    error: str | None,
    metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a canonical structured log record."""
    return {
        "timestamp": _utcnow_iso(),
        "session_id": session_id,
        "agent_id": agent_id or "",
        "action": action,
        "status": status,
        "latency_ms": latency_ms,
        "error": error,
        "metadata": metadata or {},
    }


# ── ObservabilityLogger ───────────────────────────────────────────────────────


class ObservabilityLogger:
    """Structured observability logger for Codex agents.

    Emits log records in JSON (machine-parseable) and/or human-readable text
    format.  Optionally persists records to the session SQLite database via the
    existing ``codex.logging.session_logger.log_event`` integration.

    Args:
        session_id:       Owning session identifier.  If *None*, falls back to
                          ``get_session_id()`` from ``codex.logging`` or
                          generates a fresh UUID.
        agent_id:         Default agent identifier attached to every record
                          unless overridden per call.
        output_format:    ``"json"`` (default), ``"text"``, or ``"both"``.
        log_level:        Minimum Python ``logging`` level for emitted records
                          (default: ``logging.INFO``).
        persist_to_db:    If *True* and ``codex.logging`` is available, also
                          persist records to the session SQLite store.
        python_logger:    Override the internal ``logging.Logger`` instance.
    """

    def __init__(
        self,
        session_id: str | None = None,
        agent_id: str | None = None,
        output_format: str = "json",
        log_level: int = logging.INFO,
        persist_to_db: bool = False,
        python_logger: logging.Logger | None = None,
    ) -> None:
        if session_id is None:
            if _SESSION_LOGGER_AVAILABLE and _get_session_id is not None:
                session_id = _get_session_id()
            else:
                session_id = str(uuid.uuid4())
        self.session_id: str = session_id
        self.agent_id: str | None = agent_id
        self._output_format: str = output_format.lower()
        self._log_level: int = log_level
        self._persist_to_db: bool = persist_to_db and _SESSION_LOGGER_AVAILABLE
        self._python_logger: logging.Logger = python_logger or _log
        self._lock: threading.Lock = threading.Lock()

    # ── Core emit ─────────────────────────────────────────────────────────────

    def _emit(self, record: dict[str, Any], level: int = logging.INFO) -> None:
        """Emit *record* to the configured outputs.  Thread-safe."""
        with self._lock:
            if level < self._log_level:
                return

            if self._output_format in ("json", "both"):
                self._python_logger.log(level, json.dumps(record, default=str))
            if self._output_format in ("text", "both"):
                latency_str = (
                    f" [{record['latency_ms']:.1f}ms]"
                    if record.get("latency_ms") is not None
                    else ""
                )
                error_str = f" error={record['error']!r}" if record.get("error") else ""
                msg = (
                    f"[{record['timestamp']}] "
                    f"{record.get('agent_id', '')} "
                    f"{record['action']} "
                    f"status={record['status']}"
                    f"{latency_str}"
                    f"{error_str}"
                )
                self._python_logger.log(level, msg)

            if self._persist_to_db and _session_log_event is not None:
                try:
                    _session_log_event(
                        self.session_id,
                        "INFO",
                        json.dumps(record, default=str),
                    )
                except Exception as exc:  # pragma: no cover – best effort
                    self._python_logger.debug("db persist failed: %s", exc)

    # ── Public API ────────────────────────────────────────────────────────────

    def log_agent_action(
        self,
        agent_id: str,
        action: str,
        status: str,
        latency_ms: float | None = None,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log a single agent action.

        Args:
            agent_id:   Identifier of the agent performing the action.
            action:     Short description of the action (e.g. ``"route_task"``).
            status:     Outcome — ``"success"``, ``"failure"``, or ``"error"``.
            latency_ms: Wall-clock duration in milliseconds.
            error:      Error message, if any.
            metadata:   Arbitrary key-value pairs for additional context.

        Example::

            obs.log_agent_action(
                "orchestrator",
                "route_task",
                "success",
                latency_ms=342.5,
                metadata={"task_type": "generate_code"},
            )
        """
        DEBUG_THRESHOLD = "debug"
        level = (
            logging.ERROR
            if status == "error"
            else (
                logging.WARNING
                if status == "failure"
                else (logging.DEBUG if status == DEBUG_THRESHOLD else logging.INFO)
            )
        )
        record = _build_record(
            session_id=self.session_id,
            agent_id=agent_id or self.agent_id,
            action=action,
            status=status,
            latency_ms=latency_ms,
            error=error,
            metadata=metadata,
        )
        self._emit(record, level=level)

    def log_workflow_event(
        self,
        workflow_id: str,
        event_type: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log a workflow lifecycle event.

        Args:
            workflow_id: GitHub Actions workflow or run identifier.
            event_type:  Event name (e.g. ``"run_started"``, ``"job_failed"``).
            details:     Optional extra details about the event.

        Example::

            obs.log_workflow_event(
                "ci-tests.yml#12345678",
                "job_failed",
                {"job": "test-suite", "exit_code": 1},
            )
        """
        record = _build_record(
            session_id=self.session_id,
            agent_id=self.agent_id,
            action=f"workflow:{event_type}",
            status="info",
            latency_ms=None,
            error=None,
            metadata={"workflow_id": workflow_id, **(details or {})},
        )
        self._emit(record, level=logging.INFO)

    def log_routing_decision(
        self,
        task: str,
        chosen_agent: str,
        confidence: float,
        alternatives: list[str] | None = None,
        latency_ms: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log a routing decision made by the orchestrator.

        Args:
            task:         Task description or type.
            chosen_agent: The agent selected to handle the task.
            confidence:   Confidence score in [0.0, 1.0].
            alternatives: Agents considered but not selected.
            latency_ms:   Time taken to make the routing decision.
            metadata:     Additional context.

        Example::

            obs.log_routing_decision(
                task="fix_ci_failure",
                chosen_agent="ci-auto-healer-agent",
                confidence=0.97,
                alternatives=["ci-testing-agent"],
                latency_ms=82.3,
            )
        """
        record = _build_record(
            session_id=self.session_id,
            agent_id=chosen_agent,
            action="routing_decision",
            status="success",
            latency_ms=latency_ms,
            error=None,
            metadata={
                "task": task,
                "confidence": confidence,
                "alternatives": alternatives or [],
                **(metadata or {}),
            },
        )
        conf_normalized = confidence / 100.0 if confidence > 1.0 else confidence
        self._emit(record, level=logging.DEBUG if conf_normalized >= 0.8 else logging.WARNING)

    def debug(self, agent_id: str, action: str, **kwargs: Any) -> None:
        """Convenience: log at DEBUG level."""
        self.log_agent_action(agent_id, action, "debug", **kwargs)

    def info(self, agent_id: str, action: str, **kwargs: Any) -> None:
        """Convenience: log at INFO level."""
        self.log_agent_action(agent_id, action, "success", **kwargs)

    def warning(self, agent_id: str, action: str, **kwargs: Any) -> None:
        """Convenience: log at WARNING level."""
        self.log_agent_action(agent_id, action, "failure", **kwargs)

    def error(self, agent_id: str, action: str, **kwargs: Any) -> None:
        """Convenience: log at ERROR level."""
        self.log_agent_action(agent_id, action, "error", **kwargs)


__all__ = ["ObservabilityLogger"]
