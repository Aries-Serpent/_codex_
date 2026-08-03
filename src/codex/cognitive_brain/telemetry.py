"""Structured telemetry for Cognitive Brain planner decisions.

Every negotiation, policy scoring, orchestration, and fallback event is
emitted as a JSON-serialisable :class:`TelemetryEvent`.  Events can be
consumed by:

- The built-in :class:`InMemoryTelemetryBackend` (default; suitable for tests)
- A file-based NDJSON sink
- Any custom :class:`TelemetryBackend` implementation

Usage::

    telemetry = CognitiveTelemetry()
    telemetry.record(TelemetryEvent(
        event_type="negotiation",
        model_id="claude-haiku-4.5",
        payload={"stripped": ["reasoning_effort"], "fallback": "claude-sonnet-5"},
    ))
    events = telemetry.query(event_type="negotiation")
"""

from __future__ import annotations

import abc
import json
import logging
import threading
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Event model
# ---------------------------------------------------------------------------


@dataclass
class TelemetryEvent:
    """A single structured telemetry event."""

    event_type: str  # e.g. "negotiation", "policy_score", "orchestration", "fallback"
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    session_id: Optional[str] = None
    model_id: Optional[str] = None
    task_intent: Optional[str] = None
    duration_ms: Optional[float] = None
    success: Optional[bool] = None
    # Decision forensics fields (Phase 2E)
    decision_id: Optional[str] = None
    turn_id: Optional[str] = None
    task_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)


# ---------------------------------------------------------------------------
# Backend abstraction
# ---------------------------------------------------------------------------


class TelemetryBackend(abc.ABC):
    """Abstract sink for :class:`TelemetryEvent` objects."""

    @abc.abstractmethod
    def write(self, event: TelemetryEvent) -> None: ...

    @abc.abstractmethod
    def read_all(self) -> List[TelemetryEvent]: ...


class InMemoryTelemetryBackend(TelemetryBackend):
    """Thread-safe in-memory backend.  Suitable for testing and development."""

    def __init__(self, max_events: int = 10_000) -> None:
        self._lock = threading.Lock()
        self._events: deque[TelemetryEvent] = deque(maxlen=max_events)

    def write(self, event: TelemetryEvent) -> None:
        with self._lock:
            self._events.append(event)  # O(1); deque auto-evicts oldest when full

    def read_all(self) -> List[TelemetryEvent]:
        with self._lock:
            return list(self._events)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


class NDJSONTelemetryBackend(TelemetryBackend):
    """Append-only NDJSON file sink.

    Parameters
    ----------
    path:
        Destination file.  Parent directory is created on first write.
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._lock = threading.Lock()

    def write(self, event: TelemetryEvent) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(event.to_json() + "\n")

    def read_all(self) -> List[TelemetryEvent]:
        if not self._path.exists():
            return []
        events: List[TelemetryEvent] = []
        _known_fields = {f.name for f in TelemetryEvent.__dataclass_fields__.values()}
        with self._lock:
            with self._path.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            # Strip unknown keys for backward-compat with
                            # records written by older schema versions.
                            filtered = {k: v for k, v in data.items() if k in _known_fields}
                            events.append(TelemetryEvent(**filtered))
                        except Exception:  # noqa: BLE001
                            pass
        return events


# ---------------------------------------------------------------------------
# CognitiveTelemetry façade
# ---------------------------------------------------------------------------


class CognitiveTelemetry:
    """Façade over one or more :class:`TelemetryBackend` instances.

    Parameters
    ----------
    backends:
        One or more backends to write events to.  Defaults to a single
        :class:`InMemoryTelemetryBackend`.
    session_id:
        Optional session identifier injected into every emitted event.
    """

    def __init__(
        self,
        backends: Optional[Sequence[TelemetryBackend]] = None,
        session_id: Optional[str] = None,
    ) -> None:
        self._backends: List[TelemetryBackend] = (
            list(backends) if backends else [InMemoryTelemetryBackend()]
        )
        self._session_id = session_id

    # ------------------------------------------------------------------
    # Emit helpers
    # ------------------------------------------------------------------

    def record(self, event: TelemetryEvent) -> None:
        """Write *event* to all configured backends."""
        if self._session_id and event.session_id is None:
            event.session_id = self._session_id
        for backend in self._backends:
            try:
                backend.write(event)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Telemetry backend write failed: %s", exc)

    def negotiation(
        self,
        model_id: str,
        stripped: List[str],
        fallback_used: bool,
        resolved_model: str,
        duration_ms: Optional[float] = None,
    ) -> None:
        """Emit a model-negotiation event."""
        self.record(
            TelemetryEvent(
                event_type="negotiation",
                model_id=model_id,
                duration_ms=duration_ms,
                success=True,
                payload={
                    "stripped_params": stripped,
                    "fallback_used": fallback_used,
                    "resolved_model": resolved_model,
                },
            )
        )

    def policy_score(
        self,
        task_intent: str,
        plan_id: str,
        scores: Dict[str, float],
        winner: bool = False,
        duration_ms: Optional[float] = None,
    ) -> None:
        """Emit a policy-scoring event."""
        self.record(
            TelemetryEvent(
                event_type="policy_score",
                task_intent=task_intent,
                duration_ms=duration_ms,
                success=True,
                payload={"plan_id": plan_id, "scores": scores, "winner": winner},
            )
        )

    def orchestration(
        self,
        task_intent: str,
        primary_tool: Optional[str],
        plan_notes: List[str],
        duration_ms: Optional[float] = None,
    ) -> None:
        """Emit an orchestration-plan event."""
        self.record(
            TelemetryEvent(
                event_type="orchestration",
                task_intent=task_intent,
                duration_ms=duration_ms,
                success=primary_tool is not None,
                payload={"primary_tool": primary_tool, "notes": plan_notes},
            )
        )

    def fallback(
        self,
        label: str,
        attempts: int,
        succeeded: bool,
        final_strategy: Optional[str],
        duration_ms: Optional[float] = None,
    ) -> None:
        """Emit a fallback-chain execution event."""
        self.record(
            TelemetryEvent(
                event_type="fallback",
                duration_ms=duration_ms,
                success=succeeded,
                payload={
                    "label": label,
                    "attempts": attempts,
                    "final_strategy": final_strategy,
                },
            )
        )

    def startup(self, version: str, config_summary: Dict[str, Any]) -> None:
        """Emit the brain-loaded startup event."""
        self.record(
            TelemetryEvent(
                event_type="startup",
                success=True,
                payload={"version": version, "config": config_summary},
                notes=["Cognitive Brain runtime loaded"],
            )
        )

    def forensics(
        self,
        decision_id: str,
        turn_id: Optional[str],
        task_id: Optional[str],
        selected_toolchain: Optional[str],
        rejected_alternatives: Optional[List[str]],
        negotiation_outcome: Optional[str],
        *,
        model_id: Optional[str] = None,
        task_intent: Optional[str] = None,
        duration_ms: Optional[float] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Emit a traceable decision-forensics event.

        Parameters
        ----------
        decision_id:
            Unique ID for this decision (UUID recommended).
        turn_id:
            Agent turn identifier for cross-referencing turn logs.
        task_id:
            Task or PR-level identifier.
        selected_toolchain:
            Tool surface chosen (e.g. ``"github_mcp"``).
        rejected_alternatives:
            Tool surfaces that were considered but not chosen.
        negotiation_outcome:
            Short description of the model negotiation result.
        """
        self.record(
            TelemetryEvent(
                event_type="forensics",
                model_id=model_id,
                task_intent=task_intent,
                duration_ms=duration_ms,
                success=True,
                decision_id=decision_id,
                turn_id=turn_id,
                task_id=task_id,
                payload={
                    "selected_toolchain": selected_toolchain,
                    "rejected_alternatives": rejected_alternatives or [],
                    "negotiation_outcome": negotiation_outcome,
                    **(extra or {}),
                },
            )
        )

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query(
        self,
        event_type: Optional[str] = None,
        model_id: Optional[str] = None,
        task_intent: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[TelemetryEvent]:
        """Return events matching the given filters from the first backend."""
        if not self._backends:
            return []
        all_events = self._backends[0].read_all()
        results = [
            e
            for e in all_events
            if (event_type is None or e.event_type == event_type)
            and (model_id is None or e.model_id == model_id)
            and (task_intent is None or e.task_intent == task_intent)
        ]
        if limit is not None:
            results = results[-limit:]
        return results
