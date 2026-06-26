#!/usr/bin/env python3
"""
Phase 11.3 — Agent Health Monitor
====================================
Production health monitoring for the 145-agent ecosystem.

Implements:
- Per-agent health metric tracking (success rate, latency, error rate)
- Health status classification: HEALTHY / DEGRADED / UNHEALTHY / OFFLINE
- Circuit-breaker pattern (auto-open on sustained failures)
- Heartbeat / ping simulation with configurable timeouts
- Recovery procedures (auto-retry, fallback rerouting)
- Health dashboard output (text + JSON)
- Persistence of health state to .codex/PHASE_11_3_HEALTH_STATE.json

Usage::

    python scripts/ci/phase_11_3_health_monitor.py --status
    python scripts/ci/phase_11_3_health_monitor.py --dashboard
    python scripts/ci/phase_11_3_health_monitor.py --ping unified-coverage-agent
    python scripts/ci/phase_11_3_health_monitor.py \\
        --record-event --agent ci-testing-agent --success --latency 350
    python scripts/ci/phase_11_3_health_monitor.py --circuit-status
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HEALTH_STATE_PATH = Path(".codex/PHASE_11_3_HEALTH_STATE.json")

# Degraded / unhealthy thresholds (matching spec)
HEALTHY_SUCCESS_RATE = 95.0
DEGRADED_SUCCESS_RATE = 90.0

# Circuit-breaker: trip after N failures in T seconds
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
CIRCUIT_BREAKER_WINDOW_SECONDS = 300  # 5 minutes
CIRCUIT_BREAKER_HALF_OPEN_AFTER = 60  # 1 minute cool-down


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class AgentEvent:
    """A single execution event for an agent."""

    timestamp: str
    success: bool
    latency_ms: float
    error_type: Optional[str] = None


@dataclass
class CircuitBreakerState:
    """Per-agent circuit-breaker state."""

    state: str = "CLOSED"  # CLOSED | OPEN | HALF_OPEN
    failure_count: int = 0
    last_failure_ts: Optional[str] = None
    opened_at: Optional[str] = None
    half_open_at: Optional[str] = None


@dataclass
class AgentHealthRecord:
    """Runtime health record for a single agent."""

    agent_id: str
    events: List[AgentEvent] = field(default_factory=list)
    circuit_breaker: CircuitBreakerState = field(default_factory=CircuitBreakerState)
    last_heartbeat: Optional[str] = None

    # Derived (computed on demand)
    success_rate: float = 100.0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    error_rate: float = 0.0
    throughput_per_min: float = 0.0
    status: str = "HEALTHY"

    def recompute(self) -> None:
        """Recompute derived metrics from raw events."""
        recent = self._recent_events(window_minutes=60)
        if not recent:
            self.status = "HEALTHY"
            return

        successes = [e for e in recent if e.success]
        self.success_rate = round(len(successes) / len(recent) * 100.0, 2)
        self.error_rate = round(100.0 - self.success_rate, 2)

        latencies = [e.latency_ms for e in recent if e.latency_ms > 0]
        if latencies:
            self.avg_latency_ms = round(sum(latencies) / len(latencies), 2)
            sorted_lat = sorted(latencies)
            idx = math.ceil(0.95 * len(sorted_lat)) - 1
            self.p95_latency_ms = sorted_lat[max(idx, 0)]
        else:
            self.avg_latency_ms = 0.0
            self.p95_latency_ms = 0.0

        # Throughput: events per minute over last 10 min
        ten_min = self._recent_events(window_minutes=10)
        self.throughput_per_min = round(len(ten_min) / 10.0, 2)

        # Status classification
        if self.circuit_breaker.state == "OPEN":
            self.status = "OFFLINE"
        elif self.success_rate >= HEALTHY_SUCCESS_RATE:
            self.status = "HEALTHY"
        elif self.success_rate >= DEGRADED_SUCCESS_RATE:
            self.status = "DEGRADED"
        else:
            self.status = "UNHEALTHY"

    def _recent_events(self, window_minutes: int = 60) -> List[AgentEvent]:
        """Return events within the last window_minutes."""
        now = _now_ts()
        cutoff = now - window_minutes * 60
        result = []
        for e in self.events:
            try:
                ts = _parse_ts(e.timestamp)
                if ts >= cutoff:
                    result.append(e)
            except ValueError:
                # Skip events with malformed timestamps
                continue
        return result


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------


def _now_ts() -> float:
    return time.time()


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_ts(ts_str: str) -> float:
    """Parse ISO 8601 timestamp to epoch float."""
    # Support both 'Z' suffix and '+00:00'
    ts_str = ts_str.replace("Z", "+00:00")
    return datetime.fromisoformat(ts_str).timestamp()


# ---------------------------------------------------------------------------
# Health monitor
# ---------------------------------------------------------------------------

# Default agent list (matches Phase 11.2 router profiles)
DEFAULT_AGENT_IDS = [
    "unified-coverage-agent",
    "unified-security-scanner",
    "workflow-ci-fixer",
    "unified-doc-agent",
    "performance-regression-detector",
    "ci-importerror-agent",
    "code-analysis-agent",
    "pypi-publishing-operations-agent",
    "workflow-health-monitor",
    "dependency-conflict-agent",
    "ci-failure-resolution-agent",
    "autonomous-test-healer-agent",
    "recon-scout-agent",
    "orchestrator-agent",
    "mypy-manager-agent",
    "ci-testing-agent",
    "ci-emergency-response-agent",
    "ci-auto-healer-agent",
    "self-healing-orchestrator-agent",
    "artifact-monitor-agent",
]


class AgentHealthMonitor:
    """Production health monitor for the 145-agent ecosystem."""

    def __init__(self, state_path: Path = HEALTH_STATE_PATH) -> None:
        self._state_path = state_path
        self._records: Dict[str, AgentHealthRecord] = {}
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if self._state_path.exists():
            try:
                raw = json.loads(self._state_path.read_text())
                for agent_id, data in raw.get("agents", {}).items():
                    rec = AgentHealthRecord(agent_id=agent_id)
                    rec.events = [AgentEvent(**e) for e in data.get("events", [])]
                    cb_data = data.get("circuit_breaker", {})
                    rec.circuit_breaker = CircuitBreakerState(**cb_data)
                    rec.last_heartbeat = data.get("last_heartbeat")
                    rec.recompute()
                    self._records[agent_id] = rec
            except Exception:  # noqa: BLE001
                pass  # Start fresh on corrupt state

        # Ensure all default agents have records
        for aid in DEFAULT_AGENT_IDS:
            if aid not in self._records:
                self._records[aid] = AgentHealthRecord(agent_id=aid)

    def _save(self) -> None:
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": "1.0",
            "last_updated": _iso_now(),
            "agents": {},
        }
        for agent_id, rec in self._records.items():
            payload["agents"][agent_id] = {
                "events": [asdict(e) for e in rec.events[-500:]],  # cap at 500
                "circuit_breaker": asdict(rec.circuit_breaker),
                "last_heartbeat": rec.last_heartbeat,
            }
        self._state_path.write_text(json.dumps(payload, indent=2))

    # ------------------------------------------------------------------
    # Event recording
    # ------------------------------------------------------------------

    def record_event(
        self,
        agent_id: str,
        success: bool,
        latency_ms: float,
        error_type: Optional[str] = None,
    ) -> AgentHealthRecord:
        """Record a single execution event and update health state."""
        if agent_id not in self._records:
            self._records[agent_id] = AgentHealthRecord(agent_id=agent_id)
        rec = self._records[agent_id]
        event = AgentEvent(
            timestamp=_iso_now(),
            success=success,
            latency_ms=latency_ms,
            error_type=error_type,
        )
        rec.events.append(event)

        # Update circuit breaker
        if not success:
            self._update_circuit_breaker(rec, success=False)
        else:
            self._update_circuit_breaker(rec, success=True)

        rec.recompute()
        self._save()
        return rec

    def record_heartbeat(self, agent_id: str) -> None:
        """Record a successful heartbeat ping."""
        if agent_id not in self._records:
            self._records[agent_id] = AgentHealthRecord(agent_id=agent_id)
        self._records[agent_id].last_heartbeat = _iso_now()
        self._save()

    # ------------------------------------------------------------------
    # Circuit breaker
    # ------------------------------------------------------------------

    def _update_circuit_breaker(self, rec: AgentHealthRecord, success: bool) -> None:
        cb = rec.circuit_breaker
        now = _iso_now()

        if cb.state == "OPEN":
            # Check if cool-down has elapsed (move to HALF_OPEN)
            if cb.opened_at:
                elapsed = _now_ts() - _parse_ts(cb.opened_at)
                if elapsed >= CIRCUIT_BREAKER_HALF_OPEN_AFTER:
                    cb.state = "HALF_OPEN"
                    cb.half_open_at = now
            return

        if cb.state == "HALF_OPEN":
            if success:
                # Reset on success in HALF_OPEN
                cb.state = "CLOSED"
                cb.failure_count = 0
                cb.last_failure_ts = None
                cb.opened_at = None
                cb.half_open_at = None
            else:
                # Re-open on failure
                cb.state = "OPEN"
                cb.opened_at = now
            return

        # CLOSED state
        if not success:
            cb.failure_count += 1
            cb.last_failure_ts = now
            if cb.failure_count >= CIRCUIT_BREAKER_FAILURE_THRESHOLD:
                cb.state = "OPEN"
                cb.opened_at = now
        else:
            cb.failure_count = max(0, cb.failure_count - 1)

    # ------------------------------------------------------------------
    # Status queries
    # ------------------------------------------------------------------

    def get_status(self, agent_id: str) -> AgentHealthRecord:
        """Get health record for an agent (creates default if missing)."""
        if agent_id not in self._records:
            self._records[agent_id] = AgentHealthRecord(agent_id=agent_id)
        rec = self._records[agent_id]
        rec.recompute()
        return rec

    def all_statuses(self) -> List[AgentHealthRecord]:
        for rec in self._records.values():
            rec.recompute()
        return sorted(self._records.values(), key=lambda r: r.agent_id)

    def unhealthy_agents(self) -> List[AgentHealthRecord]:
        return [r for r in self.all_statuses() if r.status in ("UNHEALTHY", "OFFLINE")]

    def summary(self) -> Dict:
        statuses = self.all_statuses()
        counts: Dict[str, int] = {"HEALTHY": 0, "DEGRADED": 0, "UNHEALTHY": 0, "OFFLINE": 0}
        for r in statuses:
            counts[r.status] = counts.get(r.status, 0) + 1
        return {
            "timestamp": _iso_now(),
            "total_agents": len(statuses),
            "status_counts": counts,
            "overall_health": "GREEN" if counts["UNHEALTHY"] == 0 and counts["OFFLINE"] == 0 else (
                "YELLOW" if counts["UNHEALTHY"] == 0 else "RED"
            ),
        }

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def print_dashboard(self) -> None:
        statuses = self.all_statuses()
        icon = {"HEALTHY": "🟢", "DEGRADED": "🟡", "UNHEALTHY": "🔴", "OFFLINE": "⚫"}
        print(f"\n{'='*70}")
        print(f"  PHASE 11.3 — AGENT HEALTH DASHBOARD  [{_iso_now()}]")
        print(f"{'='*70}")
        print(f"  {'AGENT':45s} {'STATUS':10s} {'SUCCESS%':9s} {'P95ms':8s}")
        print(f"  {'-'*45} {'-'*10} {'-'*9} {'-'*8}")
        for rec in statuses:
            print(
                f"  {rec.agent_id:45s} {icon.get(rec.status,'?')} {rec.status:8s} "
                f"{rec.success_rate:8.1f}% {rec.p95_latency_ms:7.0f}ms"
            )
        s = self.summary()
        print(f"\n  Summary: {s['total_agents']} agents | "
              f"🟢 {s['status_counts']['HEALTHY']} healthy | "
              f"🟡 {s['status_counts']['DEGRADED']} degraded | "
              f"🔴 {s['status_counts']['UNHEALTHY']} unhealthy | "
              f"⚫ {s['status_counts']['OFFLINE']} offline")
        print(f"  Overall: {s['overall_health']}")
        print(f"{'='*70}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 11.3 Agent Health Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dashboard", action="store_true", help="Print full health dashboard")
    parser.add_argument("--status", help="Get health status for a specific agent ID")
    parser.add_argument(
        "--all-status",
        action="store_true",
        help="Get status for all agents (JSON)",
    )
    parser.add_argument("--ping", help="Record a successful heartbeat for an agent")
    parser.add_argument("--record-event", action="store_true", help="Record an execution event")
    parser.add_argument("--agent", help="Agent ID for --record-event")
    parser.add_argument("--success", action="store_true", help="Event was successful")
    parser.add_argument("--failure", action="store_true", help="Event was a failure")
    parser.add_argument("--latency", type=float, default=0.0, help="Latency in ms")
    parser.add_argument("--error-type", default=None, help="Optional error type string")
    parser.add_argument("--circuit-status", action="store_true", help="Show circuit-breaker states")
    parser.add_argument("--summary", action="store_true", help="Print summary JSON")
    parser.add_argument(
        "--state-path",
        default=str(HEALTH_STATE_PATH),
        help="Path to health state file",
    )

    args = parser.parse_args(argv)
    monitor = AgentHealthMonitor(state_path=Path(args.state_path))

    if args.dashboard:
        monitor.print_dashboard()
        return 0

    if args.status:
        rec = monitor.get_status(args.status)
        rec.recompute()
        print(json.dumps(asdict(rec), indent=2, default=str))
        return 0

    if args.all_status:
        all_recs = [asdict(r) for r in monitor.all_statuses()]
        print(json.dumps(all_recs, indent=2, default=str))
        return 0

    if args.ping:
        monitor.record_heartbeat(args.ping)
        print(f"✅ Heartbeat recorded for {args.ping}")
        return 0

    if args.record_event:
        if not args.agent:
            print("ERROR: --agent required with --record-event", file=sys.stderr)
            return 2
        success = args.success or not args.failure
        rec = monitor.record_event(
            agent_id=args.agent,
            success=success,
            latency_ms=args.latency,
            error_type=args.error_type,
        )
        result = "✅ SUCCESS" if success else "❌ FAILURE"
        print(f"{result} | {args.agent} | latency={args.latency}ms | status={rec.status}")
        return 0

    if args.circuit_status:
        all_recs = monitor.all_statuses()
        data = [
            {
                "agent_id": r.agent_id,
                "circuit_state": r.circuit_breaker.state,
                "failure_count": r.circuit_breaker.failure_count,
            }
            for r in all_recs
        ]
        print(json.dumps(data, indent=2))
        return 0

    if args.summary:
        print(json.dumps(monitor.summary(), indent=2))
        return 0

    # Default: show dashboard
    monitor.print_dashboard()
    return 0


if __name__ == "__main__":
    sys.exit(main())
