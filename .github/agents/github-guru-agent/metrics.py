"""
GitHub Guru Agent — Metrics Collector

Tracks per-session performance and capability metrics.
Stores summaries in audit_artifacts/baselines/ for trend analysis.
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CapabilityMetric:
    """Metrics for a single capability invocation."""

    capability: str
    duration_seconds: float
    success: bool
    output_summary: str = ""
    error: Optional[str] = None


@dataclass
class SessionMetrics:
    """Full metrics for one agent session."""

    session_id: str
    started_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    ended_at: Optional[datetime] = None
    capabilities_invoked: list[CapabilityMetric] = field(default_factory=list)
    total_prs_analyzed: int = 0
    total_issues_triaged: int = 0
    total_workflows_checked: int = 0
    total_hygiene_issues_found: int = 0
    total_patterns_matched: int = 0

    @property
    def total_duration_seconds(self) -> float:
        if self.ended_at is None:
            return (datetime.now(tz=timezone.utc) - self.started_at).total_seconds()
        return (self.ended_at - self.started_at).total_seconds()

    @property
    def success_rate(self) -> float:
        if not self.capabilities_invoked:
            return 1.0
        return sum(1 for c in self.capabilities_invoked if c.success) / len(
            self.capabilities_invoked
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["started_at"] = self.started_at.isoformat()
        d["ended_at"] = self.ended_at.isoformat() if self.ended_at else None
        d["total_duration_seconds"] = self.total_duration_seconds
        d["success_rate"] = self.success_rate
        return d


class MetricsCollector:
    """
    Collects and persists session metrics.

    Writes JSON summaries to audit_artifacts/baselines/ for trend tracking.
    """

    def __init__(
        self,
        session_id: str,
        baselines_dir: Optional[Path] = None,
    ):
        self._session = SessionMetrics(session_id=session_id)
        self._baselines_dir = baselines_dir or Path("audit_artifacts/baselines")
        self._capability_start_times: dict[str, float] = {}

    def start_capability(self, capability: str) -> None:
        """Record start time for a capability invocation."""
        self._capability_start_times[capability] = time.monotonic()

    def end_capability(
        self,
        capability: str,
        success: bool,
        output_summary: str = "",
        error: Optional[str] = None,
    ) -> None:
        """Record end of a capability invocation."""
        start = self._capability_start_times.pop(capability, time.monotonic())
        duration = time.monotonic() - start
        self._session.capabilities_invoked.append(
            CapabilityMetric(
                capability=capability,
                duration_seconds=duration,
                success=success,
                output_summary=output_summary,
                error=error,
            )
        )

    def record_pr_analyzed(self) -> None:
        self._session.total_prs_analyzed += 1

    def record_issue_triaged(self) -> None:
        self._session.total_issues_triaged += 1

    def record_workflow_checked(self) -> None:
        self._session.total_workflows_checked += 1

    def record_hygiene_issues(self, count: int) -> None:
        self._session.total_hygiene_issues_found += count

    def record_patterns_matched(self, count: int) -> None:
        self._session.total_patterns_matched += count

    def finalize(self) -> SessionMetrics:
        """Mark session as ended and persist metrics."""
        self._session.ended_at = datetime.now(tz=timezone.utc)
        self._persist()
        return self._session

    def _persist(self) -> None:
        """Write session metrics to baselines directory."""
        try:
            self._baselines_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
            path = self._baselines_dir / f"github_guru_session_{ts}.json"
            path.write_text(
                json.dumps(self._session.to_dict(), indent=2, default=str),
                encoding="utf-8",
            )
            logger.debug("Persisted session metrics to %s", path)
        except OSError as exc:
            logger.warning("Could not persist metrics: %s", exc)
