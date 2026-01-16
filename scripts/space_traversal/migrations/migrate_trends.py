#!/usr/bin/env python3
"""
Migrate Trends

Purpose:
    Migration script for trends

Usage:
    python scripts/space_traversal/migrations/migrate_trends.py [options]
    
    Examples:
    $ python scripts/space_traversal/migrations/migrate_trends.py --help

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


"""
import logging
logger = logging.getLogger(__name__)
Database migration system for trend storage.

Provides versioned schema migrations for the audit trend database.
Requires Python 3.7+ for annotations support.

Features:
- Decorator-based migration registration
- Automatic version tracking
- Forward-only migrations (no rollback)
- Safe execution with transactions

Example:
    from scripts.space_traversal.migrations import run_migrations
    applied = run_migrations(Path("audit_artifacts/trends.db"))
    print(f"Applied migrations: {applied}")
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Callable

__all__ = ["MIGRATIONS", "migration", "run_migrations"]

MIGRATIONS: dict[str, Callable[[sqlite3.Connection], None]] = {}


def migration(version: str):
    """
    Decorator to register a migration.

    Args:
        version: Version string (e.g., "1.5.0", "1.5.1")

    Returns:
        Decorator function that registers the migration
    """

    def decorator(func: Callable[[sqlite3.Connection], None]):
        MIGRATIONS[version] = func
        return func

    return decorator


@migration("1.5.0")
def migrate_1_5_0(conn: sqlite3.Connection) -> None:
    """Initial schema - create base tables."""
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
    """
    )


@migration("1.5.1")
def migrate_1_5_1(conn: sqlite3.Connection) -> None:
    """Add tags and annotations support."""
    # Check if columns already exist before altering
    cursor = conn.execute("PRAGMA table_info(audit_runs)")
    columns = {row[1] for row in cursor.fetchall()}

    if "tags_json" not in columns:
        conn.execute("ALTER TABLE audit_runs ADD COLUMN tags_json TEXT")

    if "annotations" not in columns:
        conn.execute("ALTER TABLE audit_runs ADD COLUMN annotations TEXT")

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS run_annotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            annotation_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (run_id) REFERENCES audit_runs(run_id)
        );
    """
    )


@migration("1.5.2")
def migrate_1_5_2(conn: sqlite3.Connection) -> None:
    """Add visualization cache table."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS viz_cache (
            cache_key TEXT PRIMARY KEY,
            chart_type TEXT NOT NULL,
            data_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_viz_cache_expires
            ON viz_cache(expires_at);
    """
    )


@migration("1.5.3")
def migrate_1_5_3(conn: sqlite3.Connection) -> None:
    """Add report metadata table for dashboard reports."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS report_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_type TEXT NOT NULL,
            generated_at TEXT NOT NULL,
            parameters_json TEXT,
            output_path TEXT,
            status TEXT DEFAULT 'completed'
        );

        CREATE INDEX IF NOT EXISTS idx_report_type
            ON report_metadata(report_type);
        CREATE INDEX IF NOT EXISTS idx_report_generated
            ON report_metadata(generated_at);
    """
    )


@migration("1.5.4")
def migrate_1_5_4(conn: sqlite3.Connection) -> None:
    """Add webhook delivery tracking."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS webhook_deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            event_type TEXT NOT NULL,
            webhook_url TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            status_code INTEGER,
            response_body TEXT,
            delivered_at TEXT DEFAULT CURRENT_TIMESTAMP,
            success INTEGER DEFAULT 0,
            FOREIGN KEY (run_id) REFERENCES audit_runs(run_id)
        );

        CREATE INDEX IF NOT EXISTS idx_webhook_run
            ON webhook_deliveries(run_id);
        CREATE INDEX IF NOT EXISTS idx_webhook_event
            ON webhook_deliveries(event_type);
        CREATE INDEX IF NOT EXISTS idx_webhook_success
            ON webhook_deliveries(success);
    """
    )


@migration("1.5.5")
def migrate_1_5_5(conn: sqlite3.Connection) -> None:
    """Add performance metrics and federation prep tables."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            stage TEXT NOT NULL,
            duration_seconds REAL NOT NULL,
            memory_mb REAL,
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (run_id) REFERENCES audit_runs(run_id)
        );

        CREATE INDEX IF NOT EXISTS idx_perf_run
            ON performance_metrics(run_id);
        CREATE INDEX IF NOT EXISTS idx_perf_stage
            ON performance_metrics(stage);

        -- Federation prep: repository metadata for multi-repo aggregation
        CREATE TABLE IF NOT EXISTS repositories (
            repo_id TEXT PRIMARY KEY,
            repo_name TEXT NOT NULL,
            repo_url TEXT,
            last_sync TEXT,
            metadata_json TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_repo_name
            ON repositories(repo_name);
    """
    )


def run_migrations(db_path: Path) -> list[str]:
    """
    Run all pending migrations.

    Args:
        db_path: Path to SQLite database

    Returns:
        List of applied migration versions
    """
    applied = []

    with sqlite3.connect(db_path) as conn:
        # Ensure schema_info table exists
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_info (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """
        )

        # Get current version
        try:
            cursor = conn.execute("SELECT value FROM schema_info WHERE key = 'schema_version'")
            current = cursor.fetchone()
            current_version = current[0] if current else "0.0.0"
        except sqlite3.OperationalError:
            current_version = "0.0.0"

        # Apply pending migrations in order
        for version in sorted(MIGRATIONS.keys()):
            if version > current_version:
                MIGRATIONS[version](conn)
                conn.execute(
                    "INSERT OR REPLACE INTO schema_info (key, value) VALUES (?, ?)",
                    ("schema_version", version),
                )
                applied.append(version)
                conn.commit()

    return applied


def get_current_version(db_path: Path) -> str:
    """
    Get current schema version from database.

    Args:
        db_path: Path to SQLite database

    Returns:
        Current schema version string
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT value FROM schema_info WHERE key = 'schema_version'")
            row = cursor.fetchone()
            return row[0] if row else "0.0.0"
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        return "0.0.0"
