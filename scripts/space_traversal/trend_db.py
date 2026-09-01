#!/usr/bin/env python3
"""
Trend Db

Purpose:
    [To be documented - Trend Db]

Usage:
    python scripts/space_traversal/trend_db.py [options]

    Examples:
    $ python scripts/space_traversal/trend_db.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

__all__ = [
    "AuditSnapshot",
    "TrendDatabase",
    "create_snapshot_from_artifacts",
]


@dataclass
class AuditSnapshot:
    """Single audit run snapshot."""

    run_id: str  # UUID or timestamp-based ID
    timestamp: float  # Unix epoch
    repo_root_sha: str  # Repository state hash
    git_commit: Optional[str]  # Git commit SHA if available
    git_branch: Optional[str]  # Git branch name
    version: str  # Pipeline version
    capabilities: dict[str, float]  # {capability_id: score}
    components: dict[str, dict]  # {capability_id: {component: value}}
    weights: dict[str, float]  # Weights used
    coverage_stats: Optional[dict]  # Coverage augmentation stats
    manifest_sha: str  # Manifest hash for integrity


class TrendDatabase:
    """SQLite-based trend storage."""

    SCHEMA_VERSION = "1.5.0"

    def __init__(self, db_path: Path | str = "audit_artifacts/trends.db"):
        """
        Initialize trend database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(
                """
                -- Schema metadata
                CREATE TABLE IF NOT EXISTS schema_info (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                -- Audit run snapshots
                CREATE TABLE IF NOT EXISTS audit_runs (
                    run_id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    repo_root_sha TEXT NOT NULL,
                    git_commit TEXT,
                    git_branch TEXT,
                    version TEXT NOT NULL,
                    weights_json TEXT NOT NULL,
                    coverage_stats_json TEXT,
                    manifest_sha TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                -- Capability scores per run
                CREATE TABLE IF NOT EXISTS capability_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    capability_id TEXT NOT NULL,
                    score REAL NOT NULL,
                    functionality REAL,
                    consistency REAL,
                    tests REAL,
                    safeguards REAL,
                    documentation REAL,
                    FOREIGN KEY (run_id) REFERENCES audit_runs(run_id),
                    UNIQUE(run_id, capability_id)
                );

                -- Indexes for common queries
                CREATE INDEX IF NOT EXISTS idx_runs_timestamp
                    ON audit_runs(timestamp);
                CREATE INDEX IF NOT EXISTS idx_runs_branch
                    ON audit_runs(git_branch);
                CREATE INDEX IF NOT EXISTS idx_scores_capability
                    ON capability_scores(capability_id);
                CREATE INDEX IF NOT EXISTS idx_scores_run
                    ON capability_scores(run_id);

                -- Insert schema version
                INSERT OR REPLACE INTO schema_info (key, value)
                VALUES ('schema_version', '1.5.0');
            """
            )

    def store_snapshot(self, snapshot: AuditSnapshot) -> str:
        """
        Store an audit snapshot.

        Args:
            snapshot: AuditSnapshot to store

        Returns:
            run_id of stored snapshot
        """
        with sqlite3.connect(self.db_path) as conn:
            # Insert run metadata
            conn.execute(
                """
                INSERT INTO audit_runs
                (run_id, timestamp, repo_root_sha, git_commit, git_branch,
                 version, weights_json, coverage_stats_json, manifest_sha)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    snapshot.run_id,
                    snapshot.timestamp,
                    snapshot.repo_root_sha,
                    snapshot.git_commit,
                    snapshot.git_branch,
                    snapshot.version,
                    json.dumps(snapshot.weights),
                    json.dumps(snapshot.coverage_stats) if snapshot.coverage_stats else None,
                    snapshot.manifest_sha,
                ),
            )

            # Insert capability scores
            for cap_id, score in snapshot.capabilities.items():
                components = snapshot.components.get(cap_id, {})
                conn.execute(
                    """
                    INSERT INTO capability_scores
                    (run_id, capability_id, score, functionality, consistency,
                     tests, safeguards, documentation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        snapshot.run_id,
                        cap_id,
                        score,
                        components.get("functionality"),
                        components.get("consistency"),
                        components.get("tests"),
                        components.get("safeguards"),
                        components.get("documentation"),
                    ),
                )

            conn.commit()

        return snapshot.run_id

    def get_trend(
        self,
        capability_id: str,
        limit: int = 30,
        branch: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Get score trend for a capability.

        Args:
            capability_id: Capability ID to get trend for
            limit: Maximum number of records to return
            branch: Optional branch filter

        Returns:
            List of trend entries with timestamp, score, and components
        """
        query = """
            SELECT r.timestamp, r.git_commit, r.git_branch, cs.score,
                   cs.functionality, cs.consistency, cs.tests,
                   cs.safeguards, cs.documentation
            FROM capability_scores cs
            JOIN audit_runs r ON cs.run_id = r.run_id
            WHERE cs.capability_id = ?
        """
        params: list[Any] = [capability_id]

        if branch:
            query += " AND r.git_branch = ?"
            params.append(branch)

        query += " ORDER BY r.timestamp DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_latest_scores(self) -> dict[str, float]:
        """
        Get most recent scores for all capabilities.

        Returns:
            Dictionary mapping capability_id to latest score
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT cs.capability_id, cs.score
                FROM capability_scores cs
                JOIN (
                    SELECT capability_id, MAX(r.timestamp) as max_ts
                    FROM capability_scores cs2
                    JOIN audit_runs r ON cs2.run_id = r.run_id
                    GROUP BY capability_id
                ) latest ON cs.capability_id = latest.capability_id
                JOIN audit_runs r ON cs.run_id = r.run_id
                    AND r.timestamp = latest.max_ts
            """
            )
            return {row[0]: row[1] for row in cursor.fetchall()}

    def get_regressions(
        self,
        threshold: float = 0.02,
        lookback_runs: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Detect score regressions compared to recent history.

        Args:
            threshold: Minimum delta to consider as regression
            lookback_runs: Number of previous runs to compare against

        Returns:
            List of regression details sorted by severity
        """
        regressions = []

        with sqlite3.connect(self.db_path) as conn:
            # Get all capabilities
            caps = conn.execute("SELECT DISTINCT capability_id FROM capability_scores").fetchall()

            for (cap_id,) in caps:
                trend = self.get_trend(cap_id, limit=lookback_runs + 1)
                if len(trend) < 2:
                    continue

                current = trend[0]["score"]
                previous_scores = [t["score"] for t in trend[1:]]
                previous_avg = sum(previous_scores) / len(previous_scores)
                delta = current - previous_avg

                if delta < -threshold:
                    regressions.append(
                        {
                            "capability_id": cap_id,
                            "current_score": current,
                            "previous_avg": previous_avg,
                            "delta": delta,
                            "severity": "high" if delta < -0.05 else "medium",
                        }
                    )

        return sorted(regressions, key=lambda x: x["delta"])

    def get_run_count(self) -> int:
        """Get total number of stored audit runs."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM audit_runs")
            return cursor.fetchone()[0]

    def get_capability_ids(self) -> list[str]:
        """Get all tracked capability IDs."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT DISTINCT capability_id FROM capability_scores ORDER BY capability_id"
            )
            return [row[0] for row in cursor.fetchall()]

    def get_schema_version(self) -> str:
        """Get current schema version."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT value FROM schema_info WHERE key = 'schema_version'")
            row = cursor.fetchone()
            return row[0] if row else "unknown"

    def export_csv(self, output_path: Path, capability_id: Optional[str] = None) -> None:
        """
        Export trend data to CSV.

        Args:
            output_path: Path for output CSV file
            capability_id: Optional filter for specific capability
        """
        import csv

        query = """
            SELECT r.timestamp, r.git_commit, r.git_branch, r.version,
                   cs.capability_id, cs.score, cs.functionality, cs.consistency,
                   cs.tests, cs.safeguards, cs.documentation
            FROM capability_scores cs
            JOIN audit_runs r ON cs.run_id = r.run_id
        """
        params: list[Any] = []

        if capability_id:
            query += " WHERE cs.capability_id = ?"
            params.append(capability_id)

        query += " ORDER BY r.timestamp DESC, cs.capability_id"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

        if not rows:
            # Create empty file with headers
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                simple_writer = csv.writer(f)
                simple_writer.writerow(
                    [
                        "timestamp",
                        "git_commit",
                        "git_branch",
                        "version",
                        "capability_id",
                        "score",
                        "functionality",
                        "consistency",
                        "tests",
                        "safeguards",
                        "documentation",
                    ]
                )
            return

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            dict_writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            dict_writer.writeheader()
            dict_writer.writerows([dict(row) for row in rows])

    def cleanup_old_runs(self, max_runs: int = 1000, max_age_days: int = 365) -> int:
        """
        Clean up old audit runs based on retention policy.

        Args:
            max_runs: Maximum number of runs to keep
            max_age_days: Maximum age of runs in days

        Returns:
            Number of runs deleted
        """
        import time

        deleted = 0
        cutoff_timestamp = time.time() - (max_age_days * 86400)

        with sqlite3.connect(self.db_path) as conn:
            # Delete runs older than max_age_days
            cursor = conn.execute(
                """
                DELETE FROM audit_runs
                WHERE timestamp < ?
            """,
                (cutoff_timestamp,),
            )
            deleted += cursor.rowcount

            # Delete excess runs beyond max_runs
            cursor = conn.execute(
                """
                DELETE FROM audit_runs
                WHERE run_id NOT IN (
                    SELECT run_id FROM audit_runs
                    ORDER BY timestamp DESC
                    LIMIT ?
                )
            """,
                (max_runs,),
            )
            deleted += cursor.rowcount

            # Clean up orphaned capability scores
            conn.execute(
                """
                DELETE FROM capability_scores
                WHERE run_id NOT IN (SELECT run_id FROM audit_runs)
            """
            )

            conn.commit()

        return deleted


def create_snapshot_from_artifacts(
    artifacts_dir: Path,
    git_commit: Optional[str] = None,
    git_branch: Optional[str] = None,
) -> AuditSnapshot:
    """
    Create AuditSnapshot from audit artifacts.

    Args:
        artifacts_dir: Directory containing audit artifacts
        git_commit: Git commit SHA (optional, auto-detected if possible)
        git_branch: Git branch name (optional, auto-detected if possible)

    Returns:
        AuditSnapshot populated from artifacts
    """
    # Load capabilities_scored.json
    scored_path = artifacts_dir / "capabilities_scored.json"
    with open(scored_path, encoding="utf-8") as f:
        scored_data = json.load(f)

    # Load manifest
    manifest_path = artifacts_dir.parent / "audit_run_manifest.json"
    if not manifest_path.exists():
        manifest_path = artifacts_dir / "audit_run_manifest.json"

    manifest: dict[str, Any] = {}
    if manifest_path.exists():
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

    # Extract capabilities and components
    capabilities: dict[str, float] = {}
    components: dict[str, dict] = {}
    for cap in scored_data.get("capabilities", []):
        cap_id = cap["id"]
        capabilities[cap_id] = cap["score"]
        components[cap_id] = cap.get("components", {})

    # Get manifest SHA from first artifact
    artifacts_list = manifest.get("artifacts", [])
    manifest_sha = artifacts_list[0].get("sha", "") if artifacts_list else ""

    return AuditSnapshot(
        run_id=str(uuid.uuid4()),
        timestamp=manifest.get("timestamp", datetime.now().timestamp()),
        repo_root_sha=manifest.get("repo_root_sha", ""),
        git_commit=git_commit,
        git_branch=git_branch,
        version=manifest.get("version", "1.5.0"),
        capabilities=capabilities,
        components=components,
        weights=manifest.get("weights", {}),
        coverage_stats=manifest.get("coverage_stats"),
        manifest_sha=manifest_sha,
    )
