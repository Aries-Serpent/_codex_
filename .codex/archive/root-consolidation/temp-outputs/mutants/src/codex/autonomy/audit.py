"""
Phase 5 — Observability and Audit Plane

Every autonomous run must emit a minimum audit record to an NDJSON log.
The :class:`AuditLogger` writes structured records and accumulates
in-memory metrics counters that can be flushed to the metrics log.

Minimum audit record fields (blueprint Phase 5):
    ts, surface_id, mode, actor, event_type, token_source, runner_class,
    mutation_class, prompt_id, decision, policy_reason, target, run_id

Usage::

    from codex.autonomy.audit import AuditLogger, AuditRecord
    from codex.autonomy.registry import AutonomyMode

    logger = AuditLogger.default()
    logger.record(AuditRecord(
        surface_id="AUT-007",
        mode=AutonomyMode.SAFE_AUTO,
        actor="mbaetiong",
        event_type="issue_comment",
        token_source="github_app",
        runner_class="hosted",
        mutation_class="ADVISORY_WRITE",
        prompt_id="system-copilot-agent",
        decision="allow",
        policy_reason="allowed",
        target="PR#4254",
        run_id="25329390481",
    ))
    logger.flush_metrics()

Blueprint: .codex/docs/AUTONOMY_BLUEPRINT.md — Phase 5
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .registry import AutonomyMode, AutonomyRegistry

logger = logging.getLogger(__name__)

_DEFAULT_AUDIT_PATH = Path(".codex/autonomy_audit.ndjson")
_DEFAULT_METRICS_PATH = Path(".codex/autonomy_metrics.ndjson")


@dataclass
class AuditRecord:
    """
    Minimum audit record for one autonomous action.

    All fields are optional except those that carry the core decision context.
    """

    surface_id: str = ""
    mode: AutonomyMode = AutonomyMode.SAFE_AUTO
    actor: str = ""
    event_type: str = ""
    token_source: str = ""
    runner_class: str = "hosted"
    mutation_class: str = "READ_ONLY"
    prompt_id: str = ""
    decision: str = "allow"  # allow | deny | dry_run
    policy_reason: str = ""
    target: str = ""
    run_id: str = ""
    # Auto-populated fields
    ts: float = field(default_factory=time.time)
    record_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> dict[str, Any]:
        return {
            "ts": self.ts,
            "record_id": self.record_id,
            "surface_id": self.surface_id,
            "mode": self.mode.value if isinstance(self.mode, AutonomyMode) else self.mode,
            "actor": self.actor,
            "event_type": self.event_type,
            "token_source": self.token_source,
            "runner_class": self.runner_class,
            "mutation_class": self.mutation_class,
            "prompt_id": self.prompt_id,
            "decision": self.decision,
            "policy_reason": self.policy_reason,
            "target": self.target,
            "run_id": self.run_id,
        }


@dataclass
class MetricsSnapshot:
    """Aggregated metrics from an audit session."""

    autonomy_mode_count: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    surface_invocation_count: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    mutation_count_by_class: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    token_source_count: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    runner_class_count: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    deny_count_by_policy: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    dispatch_event_count: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    prompt_family_count: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    total_records: int = 0
    dry_run_count: int = 0
    approval_bypass_attempts: int = 0

    @property
    def dry_run_ratio(self) -> float:
        if self.total_records == 0:
            return 0.0
        return self.dry_run_count / self.total_records

    def to_dict(self) -> dict[str, Any]:
        return {
            "ts": time.time(),
            "total_records": self.total_records,
            "dry_run_ratio": self.dry_run_ratio,
            "approval_bypass_attempts": self.approval_bypass_attempts,
            "autonomy_mode_count": dict(self.autonomy_mode_count),
            "surface_invocation_count": dict(self.surface_invocation_count),
            "mutation_count_by_class": dict(self.mutation_count_by_class),
            "token_source_count": dict(self.token_source_count),
            "runner_class_count": dict(self.runner_class_count),
            "deny_count_by_policy": dict(self.deny_count_by_policy),
            "dispatch_event_count": dict(self.dispatch_event_count),
            "prompt_family_count": dict(self.prompt_family_count),
        }


class AuditLogger:
    """
    Writes audit records to NDJSON and accumulates metrics.

    Thread safety: single-writer only (no locking).  For concurrent use,
    each session should create its own logger instance.
    """

    def __init__(
        self,
        audit_path: Optional[Path] = None,
        metrics_path: Optional[Path] = None,
        registry: Optional[AutonomyRegistry] = None,
    ) -> None:
        reg = registry or AutonomyRegistry.load()
        self._audit_path = audit_path or (
            Path(reg.audit_log_path) if reg.audit_log_path else _DEFAULT_AUDIT_PATH
        )
        self._metrics_path = metrics_path or (
            Path(reg.metrics_log_path) if reg.metrics_log_path else _DEFAULT_METRICS_PATH
        )
        self._metrics = MetricsSnapshot()

    @classmethod
    def default(cls) -> "AuditLogger":
        return cls()

    # ── Core record API ───────────────────────────────────────────────────────

    def record(self, rec: AuditRecord) -> None:
        """Append *rec* to the audit NDJSON log and update in-memory metrics."""
        self._update_metrics(rec)
        self._write_ndjson(self._audit_path, rec.to_dict())

    def _update_metrics(self, rec: AuditRecord) -> None:
        m = self._metrics
        m.total_records += 1
        mode_val = rec.mode.value if isinstance(rec.mode, AutonomyMode) else str(rec.mode)
        m.autonomy_mode_count[mode_val] += 1
        if rec.surface_id:
            m.surface_invocation_count[rec.surface_id] += 1
        if rec.mutation_class:
            m.mutation_count_by_class[rec.mutation_class] += 1
        if rec.token_source:
            m.token_source_count[rec.token_source] += 1
        if rec.runner_class:
            m.runner_class_count[rec.runner_class] += 1
        if rec.event_type:
            m.dispatch_event_count[rec.event_type] += 1
        if rec.prompt_id:
            m.prompt_family_count[rec.prompt_id] += 1
        if rec.decision == "deny":
            reason_key = rec.policy_reason[:40] if rec.policy_reason else "unknown"
            m.deny_count_by_policy[reason_key] += 1
        if rec.decision == "dry_run":
            m.dry_run_count += 1

    def flush_metrics(self) -> None:
        """Write current metrics snapshot to the metrics NDJSON log."""
        self._write_ndjson(self._metrics_path, self._metrics.to_dict())
        logger.info(
            "AuditLogger: flushed metrics — %d records, dry_run_ratio=%.2f",
            self._metrics.total_records,
            self._metrics.dry_run_ratio,
        )

    @property
    def metrics(self) -> MetricsSnapshot:
        return self._metrics

    def audit_coverage(self, total_runs: int) -> float:
        """
        Estimate audit coverage as fraction of *total_runs* that were recorded.

        Used by the Phase 6 expansion gate.
        """
        if total_runs <= 0:
            return 0.0
        return min(1.0, self._metrics.total_records / total_runs)

    # ── I/O helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _write_ndjson(path: Path, data: dict[str, Any]) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(data, default=str) + "\n")
        except OSError as exc:
            logger.warning("AuditLogger: failed to write %s: %s", path, exc)
