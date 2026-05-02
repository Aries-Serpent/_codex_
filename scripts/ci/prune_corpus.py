"""
scripts/ci/prune_corpus.py
Phase 3 — Configurable retention policy for the SQLite agent memory corpus.

Removes agent_sessions entries older than RETENTION_DAYS from .codex/codex_corpus.db
and logs the pruning operation to the accountability report.

The retention window defaults to 90 days and can be overridden by setting the
COGNITIVE_BRAIN_LTM_RETENTION_DAYS repository variable without a code change.

Usage:
  python scripts/ci/prune_corpus.py               # dry-run (default)
  python scripts/ci/prune_corpus.py --apply        # apply deletions
  python scripts/ci/prune_corpus.py --stats        # print corpus statistics

Exit codes:
  0  — success (or no-op in dry-run)
  1  — database error
"""

from __future__ import annotations

import argparse
import datetime
import os
import pathlib
import sqlite3
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / ".codex" / "codex_corpus.db"
# Wired to COGNITIVE_BRAIN_LTM_RETENTION_DAYS repo variable (P2.2) so the
# retention window can be adjusted without a code change.  Defaults to 90 days.
# Defensive: float() handles "90.0"; int() handles integers; falls back to 90
# if the variable is absent or contains a non-numeric value.
try:
    RETENTION_DAYS: int = int(float(os.environ.get("COGNITIVE_BRAIN_LTM_RETENTION_DAYS", "90")))
except (ValueError, TypeError):
    import warnings as _w

    _w.warn(
        "COGNITIVE_BRAIN_LTM_RETENTION_DAYS is not a valid number; defaulting to 90 days",
        RuntimeWarning,
        stacklevel=1,
    )
    RETENTION_DAYS = 90


def get_stats(conn: sqlite3.Connection) -> dict:
    """Return corpus statistics from the database."""
    try:
        total = conn.execute("SELECT COUNT(*) FROM agent_sessions").fetchone()[0]
        stale = conn.execute(
            "SELECT COUNT(*) FROM agent_sessions WHERE start_time < datetime('now', ?)",
            (f"-{RETENTION_DAYS} days",),
        ).fetchone()[0]
        oldest = conn.execute("SELECT MIN(start_time) FROM agent_sessions").fetchone()[0]
        return {"total": total, "stale": stale, "oldest": oldest}
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return {"total": 0, "stale": 0, "oldest": None}


def print_stats(conn: sqlite3.Connection) -> None:
    """Print corpus statistics."""
    stats = get_stats(conn)
    print(f"Corpus statistics ({DB_PATH.name}):")
    print(f"  Total sessions:     {stats['total']}")
    print(f"  Stale (>{RETENTION_DAYS}d): {stats['stale']}")
    print(f"  Oldest session:     {stats['oldest'] or 'N/A'}")
    print(f"  Retention policy:   {RETENTION_DAYS} days")


def prune(apply: bool = False) -> int:
    """
    Prune stale sessions from the corpus.

    Args:
        apply: If False, dry-run (print what would be deleted).

    Returns:
        Number of sessions pruned (or would-be pruned in dry-run).
    """
    if not DB_PATH.exists():
        print(f"ℹ️  Database not found: {DB_PATH}")
        print("   Nothing to prune — database will be created when build_embeddings.py runs.")
        return 0

    try:
        conn = sqlite3.connect(DB_PATH)
    except sqlite3.Error as exc:
        print(f"ERROR: Cannot open database: {exc}")
        sys.exit(1)

    try:
        stats = get_stats(conn)
        stale_count = stats["stale"]

        if stale_count == 0:
            print(f"✅ Corpus is clean — no sessions older than {RETENTION_DAYS} days.")
            conn.close()
            return 0

        if apply:
            conn.execute(
                "DELETE FROM agent_sessions WHERE start_time < datetime('now', ?)",
                (f"-{RETENTION_DAYS} days",),
            )
            conn.execute("VACUUM")
            conn.commit()
            pruned = stale_count
            print(
                f"✅ Pruned {pruned} session(s) older than {RETENTION_DAYS} days "
                f"from {DB_PATH.name}"
            )
            # Log the prune to accountability report
            _log_prune_event(pruned)
        else:
            pruned = stale_count
            print(
                f"DRY-RUN: Would prune {pruned} session(s) older than "
                f"{RETENTION_DAYS} days from {DB_PATH.name}"
            )
            print(f"         Oldest session: {stats['oldest']}")
            print("         Run with --apply to execute.")

        conn.close()
        return pruned
    except sqlite3.Error as exc:
        print(f"ERROR: Database operation failed: {exc}")
        conn.close()
        sys.exit(1)


def _log_prune_event(pruned_count: int) -> None:
    """Append a prune event record to the SQLite log table (if it exists)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS prune_log "
            "(timestamp TEXT, pruned_count INTEGER, retention_days INTEGER)"
        )
        conn.execute(
            "INSERT INTO prune_log VALUES (?, ?, ?)",
            (
                datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                pruned_count,
                RETENTION_DAYS,
            ),
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as exc:  # noqa: BLE001
        # Log failure is non-fatal — prune was already applied successfully.
        # Log to stderr so the issue is visible without failing the prune.
        import sys

        print(f"Warning: Could not log prune event: {exc}", file=sys.stderr)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description=f"Prune agent_sessions entries older than {RETENTION_DAYS} days"
    )
    ap.add_argument("--apply", action="store_true", help="Apply deletions (default: dry-run)")
    ap.add_argument("--stats", action="store_true", help="Print corpus statistics and exit")
    args = ap.parse_args()

    if args.stats:
        if not DB_PATH.exists():
            print(f"Database not found: {DB_PATH}")
            sys.exit(0)
        conn = sqlite3.connect(DB_PATH)
        print_stats(conn)
        conn.close()
        sys.exit(0)

    prune(apply=args.apply)
