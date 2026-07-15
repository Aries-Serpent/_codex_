#!/usr/bin/env python3
"""
CASCADE DETECTION & PREVENTION SYSTEM (Phase 3 & 4 Hardening)
─────────────────────────────────────────────────────────────

Incident: PR #5324 experienced 46 cascading Copilot errors across three waves.

Architecture:
  Phase 3: Cascade Detection & Monitoring
    - Real-time error pattern detection (>3 errors in <60 seconds)
    - Cascade classification (Wave 1, Wave 2, Wave 3 escalation)
    - Telemetry collection and analysis

  Phase 4: Prevention & Circuit Breaking
    - Circuit breaker for Copilot comment processing
    - Error rate limiting (max 5 error comments per PR per hour)
    - Exponential backoff and automatic pause/resume
    - Safeguards against recursive error generation

Database:
  cascade_events: event_id, pr_number, timestamp, error_count, wave, status
  circuit_breaker_state: pr_number, state, last_error_time, error_count, paused_until
  error_comments: comment_id, pr_number, error_type, created_at, wave
"""

from __future__ import annotations

import json
import logging
import sqlite3
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# ENUMS & CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────


class CircuitBreakerState(Enum):
    """Circuit breaker operational states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Error threshold exceeded, paused
    HALF_OPEN = "half_open"  # Recovery attempt in progress
    ARMED = "armed"  # Monitoring mode (pre-incident)


class CascadeWave(Enum):
    """Incident escalation waves."""

    WAVE_1 = "wave_1"  # Initial errors (3-9 errors)
    WAVE_2 = "wave_2"  # Rapid escalation (10-25 errors)
    WAVE_3 = "wave_3"  # Critical cascade (26+ errors)


# ─────────────────────────────────────────────────────────────────────────────
# CONFIG: THRESHOLDS & LIMITS
# ─────────────────────────────────────────────────────────────────────────────

CASCADE_CONFIG = {
    # Cascade detection thresholds
    "cascade_detection": {
        "wave_1_threshold": 3,  # errors
        "wave_1_window": 60,  # seconds
        "wave_2_threshold": 10,  # errors
        "wave_2_window": 60,  # seconds
        "wave_3_threshold": 26,  # errors
        "wave_3_window": 60,  # seconds
    },
    # Error rate limiting
    "error_limits": {
        "max_errors_per_hour": 5,  # per PR
        "max_errors_per_minute": 2,  # emergency limit
        "max_errors_per_day": 15,  # per PR
    },
    # Circuit breaker behavior
    "circuit_breaker": {
        "initial_backoff": 10,  # seconds
        "max_backoff": 300,  # 5 minutes
        "backoff_multiplier": 2.0,
        "recovery_timeout": 600,  # 10 minutes in HALF_OPEN state
    },
    # Monitoring & alerting
    "monitoring": {
        "alert_threshold": "wave_2",  # Alert when exceeding this
        "escalation_threshold": "wave_3",  # Escalate when exceeding this
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class CascadeEvent:
    """Represents a cascade detection event."""

    event_id: str
    pr_number: int
    timestamp: datetime
    error_count: int
    wave: CascadeWave
    status: str  # "detected", "mitigated", "escalated"
    details: dict[str, Any]


@dataclass
class CircuitBreakerStatus:
    """Current state of the circuit breaker for a PR."""

    pr_number: int
    state: CircuitBreakerState
    error_count: int
    last_error_time: Optional[datetime]
    paused_until: Optional[datetime]
    recovery_attempts: int
    last_state_change: datetime


@dataclass
class ErrorComment:
    """Represents an error comment posted by Copilot."""

    comment_id: int
    pr_number: int
    error_type: str  # "api_error", "parsing_error", "timeout", etc.
    created_at: datetime
    wave: Optional[CascadeWave]
    is_self_referential: bool


# ─────────────────────────────────────────────────────────────────────────────
# CASCADE DETECTION ENGINE
# ─────────────────────────────────────────────────────────────────────────────


class CascadeDetector:
    """Detects cascading error patterns in PR comment streams."""

    def __init__(self, db_path: str = ".codex/cascade_detection.db"):
        """Initialize detector with SQLite database."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cascade_events (
                    event_id TEXT PRIMARY KEY,
                    pr_number INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    error_count INTEGER NOT NULL,
                    wave TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS error_comments (
                    comment_id INTEGER PRIMARY KEY,
                    pr_number INTEGER NOT NULL,
                    error_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    wave TEXT,
                    is_self_referential BOOLEAN DEFAULT 0,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(comment_id, pr_number)
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cascade_pr_time
                ON cascade_events(pr_number, timestamp)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_error_pr_time
                ON error_comments(pr_number, created_at)
            """)

            conn.commit()

    def detect_cascade(
        self, pr_number: int, current_error_count: int
    ) -> Optional[CascadeWave]:
        """
        Detect if error count exceeds cascade thresholds.

        Args:
            pr_number: GitHub PR number
            current_error_count: Total error count on PR

        Returns:
            CascadeWave if threshold exceeded, else None
        """
        config = CASCADE_CONFIG["cascade_detection"]

        if current_error_count >= config["wave_3_threshold"]:
            return CascadeWave.WAVE_3
        elif current_error_count >= config["wave_2_threshold"]:
            return CascadeWave.WAVE_2
        elif current_error_count >= config["wave_1_threshold"]:
            return CascadeWave.WAVE_1

        return None

    def classify_errors(
        self, pr_number: int, error_comments: list[ErrorComment]
    ) -> Optional[CascadeWave]:
        """
        Classify errors into waves based on temporal clustering.

        Args:
            pr_number: GitHub PR number
            error_comments: List of error comments with timestamps

        Returns:
            Highest cascade wave detected
        """
        if not error_comments:
            return None

        config = CASCADE_CONFIG["cascade_detection"]

        # Sort by creation time
        sorted_comments = sorted(error_comments, key=lambda c: c.created_at)

        highest_wave = None

        # Check for Wave 1: 3+ errors in 60 seconds
        if len(sorted_comments) >= config["wave_1_threshold"]:
            window_start = sorted_comments[0].created_at
            window_end = window_start + timedelta(
                seconds=config["wave_1_window"]
            )
            count_in_window = sum(
                1 for c in sorted_comments if window_start <= c.created_at <= window_end
            )

            if count_in_window >= config["wave_1_threshold"]:
                highest_wave = CascadeWave.WAVE_1

        # Check for Wave 2: 10+ errors in 60 seconds
        if len(sorted_comments) >= config["wave_2_threshold"]:
            for i in range(len(sorted_comments) - config["wave_2_threshold"] + 1):
                window_start = sorted_comments[i].created_at
                window_end = window_start + timedelta(
                    seconds=config["wave_2_window"]
                )
                count_in_window = sum(
                    1
                    for c in sorted_comments
                    if window_start <= c.created_at <= window_end
                )

                if count_in_window >= config["wave_2_threshold"]:
                    highest_wave = CascadeWave.WAVE_2
                    break

        # Check for Wave 3: 26+ errors in 60 seconds
        if len(sorted_comments) >= config["wave_3_threshold"]:
            for i in range(len(sorted_comments) - config["wave_3_threshold"] + 1):
                window_start = sorted_comments[i].created_at
                window_end = window_start + timedelta(
                    seconds=config["wave_3_window"]
                )
                count_in_window = sum(
                    1
                    for c in sorted_comments
                    if window_start <= c.created_at <= window_end
                )

                if count_in_window >= config["wave_3_threshold"]:
                    highest_wave = CascadeWave.WAVE_3
                    break

        return highest_wave

    def record_error_comment(
        self,
        comment_id: int,
        pr_number: int,
        error_type: str,
        created_at: datetime,
        is_self_referential: bool = False,
    ) -> None:
        """Record an error comment for cascade analysis."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO error_comments
                (comment_id, pr_number, error_type, created_at, is_self_referential)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    comment_id,
                    pr_number,
                    error_type,
                    created_at.isoformat(),
                    is_self_referential,
                ),
            )
            conn.commit()

    def get_error_count(
        self, pr_number: int, time_window_seconds: int = 3600
    ) -> int:
        """Get error count within a time window."""
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=time_window_seconds)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM error_comments
                WHERE pr_number = ? AND created_at >= ? AND NOT is_self_referential
                """,
                (pr_number, cutoff.isoformat()),
            )
            return cursor.fetchone()[0]

    def get_recent_cascades(self, pr_number: int) -> list[CascadeEvent]:
        """Get recent cascade events for a PR."""
        cutoff = (
            datetime.now(timezone.utc) - timedelta(hours=24)
        ).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT event_id, pr_number, timestamp, error_count, wave, status, details
                FROM cascade_events
                WHERE pr_number = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                """,
                (pr_number, cutoff),
            )

            events = []
            for row in cursor.fetchall():
                events.append(
                    CascadeEvent(
                        event_id=row[0],
                        pr_number=row[1],
                        timestamp=datetime.fromisoformat(row[2]),
                        error_count=row[3],
                        wave=CascadeWave(row[4]),
                        status=row[5],
                        details=json.loads(row[6]),
                    )
                )
            return events


# ─────────────────────────────────────────────────────────────────────────────
# CIRCUIT BREAKER
# ─────────────────────────────────────────────────────────────────────────────


class CircuitBreaker:
    """
    Circuit breaker for Copilot comment processing.

    Prevents cascading errors by pausing comment generation when error
    rate exceeds thresholds, implementing exponential backoff and
    automatic recovery.
    """

    def __init__(self, db_path: str = ".codex/circuit_breaker.db"):
        """Initialize circuit breaker with state management."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS breaker_state (
                    pr_number INTEGER PRIMARY KEY,
                    state TEXT NOT NULL,
                    error_count INTEGER DEFAULT 0,
                    last_error_time TEXT,
                    paused_until TEXT,
                    recovery_attempts INTEGER DEFAULT 0,
                    last_state_change TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS backoff_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pr_number INTEGER NOT NULL,
                    transition_from TEXT NOT NULL,
                    transition_to TEXT NOT NULL,
                    backoff_seconds INTEGER NOT NULL,
                    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def get_status(self, pr_number: int) -> CircuitBreakerStatus:
        """Get current circuit breaker status for a PR."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT state, error_count, last_error_time, paused_until,
                       recovery_attempts, last_state_change
                FROM breaker_state WHERE pr_number = ?
                """,
                (pr_number,),
            )

            row = cursor.fetchone()

        if not row:
            # Initialize new breaker state
            return CircuitBreakerStatus(
                pr_number=pr_number,
                state=CircuitBreakerState.ARMED,
                error_count=0,
                last_error_time=None,
                paused_until=None,
                recovery_attempts=0,
                last_state_change=datetime.now(timezone.utc),
            )

        return CircuitBreakerStatus(
            pr_number=pr_number,
            state=CircuitBreakerState(row[0]),
            error_count=row[1],
            last_error_time=datetime.fromisoformat(row[2])
            if row[2]
            else None,
            paused_until=datetime.fromisoformat(row[3]) if row[3] else None,
            recovery_attempts=row[4],
            last_state_change=datetime.fromisoformat(row[5]),
        )

    def should_accept_comment(self, pr_number: int) -> bool:
        """
        Check if circuit breaker should accept comment generation.

        Returns:
            True if comments should be allowed, False if paused
        """
        status = self.get_status(pr_number)

        if status.state == CircuitBreakerState.CLOSED:
            return True
        elif status.state == CircuitBreakerState.OPEN:
            if status.paused_until and datetime.now(timezone.utc) > status.paused_until:
                # Transition to HALF_OPEN for recovery attempt
                self._transition_state(pr_number, CircuitBreakerState.HALF_OPEN)
                return True
            return False
        elif status.state == CircuitBreakerState.HALF_OPEN:
            return True  # Allow recovery attempt
        else:  # ARMED
            return True

    def record_error(
        self, pr_number: int, error_type: str, details: Optional[dict[str, Any]] = None
    ) -> CircuitBreakerState:
        """
        Record an error and potentially transition states.

        Args:
            pr_number: GitHub PR number
            error_type: Type of error encountered
            details: Additional error details

        Returns:
            New circuit breaker state
        """
        status = self.get_status(pr_number)
        config = CASCADE_CONFIG["circuit_breaker"]
        error_limits = CASCADE_CONFIG["error_limits"]

        # Increment error count
        new_error_count = status.error_count + 1
        now = datetime.now(timezone.utc)

        # Check rate limits
        minute_errors = self._get_errors_in_window(pr_number, 60)
        hour_errors = self._get_errors_in_window(pr_number, 3600)

        if minute_errors >= error_limits["max_errors_per_minute"]:
            # Emergency: transition to OPEN immediately
            backoff_seconds = config["max_backoff"]
            self._transition_state(
                pr_number,
                CircuitBreakerState.OPEN,
                backoff_seconds,
                new_error_count,
            )
            return CircuitBreakerState.OPEN

        if hour_errors >= error_limits["max_errors_per_hour"]:
            # Rate limit exceeded: transition to OPEN
            backoff_seconds = min(
                config["initial_backoff"] * (2 ** (status.recovery_attempts)),
                config["max_backoff"],
            )
            self._transition_state(
                pr_number,
                CircuitBreakerState.OPEN,
                backoff_seconds,
                new_error_count,
            )
            return CircuitBreakerState.OPEN

        # Update error count in CLOSED state
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO breaker_state
                (pr_number, state, error_count, last_error_time, last_state_change)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    pr_number,
                    CircuitBreakerState.CLOSED.value,
                    new_error_count,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
            conn.commit()

        return CircuitBreakerState.CLOSED

    def record_success(self, pr_number: int) -> None:
        """Record successful comment generation."""
        status = self.get_status(pr_number)

        if status.state == CircuitBreakerState.HALF_OPEN:
            # Recovery successful: transition back to CLOSED
            self._transition_state(pr_number, CircuitBreakerState.CLOSED)
        elif status.state == CircuitBreakerState.CLOSED:
            # Reset error count periodically
            if (
                status.last_error_time
                and (datetime.now(timezone.utc) - status.last_error_time).total_seconds()
                > 3600
            ):
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        UPDATE breaker_state
                        SET error_count = 0, last_error_time = NULL
                        WHERE pr_number = ?
                        """,
                        (pr_number,),
                    )
                    conn.commit()

    def _transition_state(
        self,
        pr_number: int,
        new_state: CircuitBreakerState,
        backoff_seconds: Optional[int] = None,
        error_count: Optional[int] = None,
    ) -> None:
        """Transition to a new state with optional backoff."""
        status = self.get_status(pr_number)
        now = datetime.now(timezone.utc)

        paused_until = None
        recovery_attempts = status.recovery_attempts

        if new_state == CircuitBreakerState.OPEN:
            backoff = backoff_seconds or CASCADE_CONFIG["circuit_breaker"][
                "initial_backoff"
            ]
            paused_until = (now + timedelta(seconds=backoff)).isoformat()

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO backoff_history
                    (pr_number, transition_from, transition_to, backoff_seconds)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        pr_number,
                        status.state.value,
                        new_state.value,
                        backoff,
                    ),
                )
                conn.commit()

        elif new_state == CircuitBreakerState.HALF_OPEN:
            recovery_attempts = status.recovery_attempts + 1

        elif new_state == CircuitBreakerState.CLOSED:
            recovery_attempts = 0

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO breaker_state
                (pr_number, state, error_count, paused_until, recovery_attempts, last_state_change)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    pr_number,
                    new_state.value,
                    error_count or status.error_count,
                    paused_until,
                    recovery_attempts,
                    now.isoformat(),
                ),
            )
            conn.commit()

    def _get_errors_in_window(self, pr_number: int, window_seconds: int) -> int:
        """Get error count within time window."""
        cutoff = (
            datetime.now(timezone.utc) - timedelta(seconds=window_seconds)
        ).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM backoff_history
                WHERE pr_number = ? AND triggered_at >= ?
                """,
                (pr_number, cutoff),
            )
            return cursor.fetchone()[0]


# ─────────────────────────────────────────────────────────────────────────────
# MONITORING & ALERTING
# ─────────────────────────────────────────────────────────────────────────────


class CascadeMonitor:
    """Real-time monitoring for cascade pattern detection."""

    def __init__(
        self,
        detector: CascadeDetector,
        breaker: CircuitBreaker,
    ):
        """Initialize monitor with detector and breaker."""
        self.detector = detector
        self.breaker = breaker

    def check_cascade(self, pr_number: int) -> Optional[dict[str, Any]]:
        """
        Check for cascade patterns and return alert if needed.

        Returns:
            Alert dict if cascade detected, else None
        """
        error_count = self.detector.get_error_count(pr_number, time_window_seconds=3600)
        cascade_wave = self.detector.detect_cascade(pr_number, error_count)

        if not cascade_wave:
            return None

        config = CASCADE_CONFIG["monitoring"]
        alert_threshold = CascadeWave[config["alert_threshold"].upper()]
        escalation_threshold = CascadeWave[config["escalation_threshold"].upper()]

        alert_level = "info"
        if cascade_wave.value >= escalation_threshold.value:
            alert_level = "critical"
        elif cascade_wave.value >= alert_threshold.value:
            alert_level = "warning"

        return {
            "pr_number": pr_number,
            "cascade_wave": cascade_wave.value,
            "error_count": error_count,
            "alert_level": alert_level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "breaker_status": asdict(self.breaker.get_status(pr_number)),
        }

    def emit_metrics(self, pr_number: int) -> dict[str, Any]:
        """Emit Prometheus-style metrics for monitoring."""
        status = self.breaker.get_status(pr_number)
        error_count = self.detector.get_error_count(pr_number)
        cascades = self.detector.get_recent_cascades(pr_number)

        return {
            "pr_number": pr_number,
            "breaker_state": status.state.value,
            "error_count": error_count,
            "error_count_per_hour": self.detector.get_error_count(
                pr_number, time_window_seconds=3600
            ),
            "recent_cascade_events": len(cascades),
            "highest_wave": (
                cascades[0].wave.value if cascades else None
            ),
            "breaker_recovery_attempts": status.recovery_attempts,
        }


# ─────────────────────────────────────────────────────────────────────────────
# CLI & INTEGRATION
# ─────────────────────────────────────────────────────────────────────────────


def main() -> int:
    """CLI entry point for cascade detection system."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Cascade Detection & Prevention System"
    )
    parser.add_argument("--pr", type=int, required=True, help="GitHub PR number")
    parser.add_argument(
        "--check-cascade", action="store_true", help="Check for cascade pattern"
    )
    parser.add_argument(
        "--record-error",
        type=str,
        help="Record error comment (format: comment_id,error_type)",
    )
    parser.add_argument(
        "--check-breaker", action="store_true", help="Check circuit breaker status"
    )
    parser.add_argument(
        "--metrics", action="store_true", help="Emit monitoring metrics"
    )
    parser.add_argument(
        "--db-dir",
        type=str,
        default=".codex",
        help="Database directory",
    )

    args = parser.parse_args()

    detector = CascadeDetector(f"{args.db_dir}/cascade_detection.db")
    breaker = CircuitBreaker(f"{args.db_dir}/circuit_breaker.db")
    monitor = CascadeMonitor(detector, breaker)

    if args.check_cascade:
        alert = monitor.check_cascade(args.pr)
        if alert:
            print(json.dumps(alert, indent=2))
            return 1 if alert["alert_level"] == "critical" else 0
        return 0

    if args.check_breaker:
        status = breaker.get_status(args.pr)
        print(json.dumps(asdict(status), indent=2, default=str))
        return 0

    if args.metrics:
        metrics = monitor.emit_metrics(args.pr)
        print(json.dumps(metrics, indent=2))
        return 0

    if args.record_error:
        parts = args.record_error.split(",")
        comment_id = int(parts[0])
        error_type = parts[1]
        detector.record_error_comment(
            comment_id, args.pr, error_type, datetime.now(timezone.utc)
        )
        print(f"Recorded error comment {comment_id}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
