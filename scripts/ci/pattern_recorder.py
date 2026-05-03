#!/usr/bin/env python3
"""
CI Pattern Recorder — Phase 6 (Cross-Session Pattern Knowledge Graph)

Records pattern occurrences detected by ``auto_fix_common_issues.py`` into the
cognitive brain SQLite database (``CODEX_DB_PATH``).  This enables the cognitive
brain to learn from every CI failure and build a persistent pattern history across
local Copilot sessions.

The ``patterns`` table created here mirrors the one initialised by
``cognitive_app/src/server/cli_api_server.py``; both use ``CREATE TABLE IF NOT
EXISTS`` so whichever runs first wins.

Usage
-----
    # Record patterns from a JSON diagnostic report:
    python scripts/ci/pattern_recorder.py record --report .codex/diagnostic-report.json

    # Record a single pattern occurrence directly:
    python scripts/ci/pattern_recorder.py insert \\
        --pattern-id 18 \\
        --pattern-name "Duplicate Kwargs" \\
        --file-path src/codex/quantum_orchestrator/cli.py \\
        --line 42 \\
        --description "Duplicate keyword argument 'temperature' removed" \\
        --auto-fixable --fixed

    # Query recent pattern history:
    python scripts/ci/pattern_recorder.py query --limit 20

    # Show pattern frequency summary:
    python scripts/ci/pattern_recorder.py summary

    # Export knowledge graph as JSON:
    python scripts/ci/pattern_recorder.py export --output /tmp/patterns.json

Environment
-----------
    CODEX_DB_PATH       Path to the SQLite database
                        (default: ~/.codex/cli_history.db)
    CODEX_GIT_SHA       Git SHA to tag occurrences with (optional)
    GITHUB_SHA          Fallback git SHA (set by GitHub Actions)
    GITHUB_RUN_ID       Session identifier (set by GitHub Actions)
    COPILOT_SESSION_ID  Fallback session identifier
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

_DEFAULT_DB_PATH = os.path.join(os.path.expanduser("~"), ".codex", "cli_history.db")


def _open_db(db_path: str) -> sqlite3.Connection:
    """Open the cognitive brain database, creating the ``patterns`` table if absent.

    Safe to call on an already-initialised DB — uses ``CREATE TABLE IF NOT EXISTS``.
    """
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS patterns (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_id   INTEGER NOT NULL,
            pattern_name TEXT NOT NULL,
            file_path    TEXT,
            line_number  INTEGER,
            description  TEXT NOT NULL,
            auto_fixable INTEGER NOT NULL DEFAULT 0,
            fixed        INTEGER NOT NULL DEFAULT 0,
            session      TEXT,
            git_sha      TEXT,
            timestamp    TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_patterns_name ON patterns (pattern_name)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_patterns_session ON patterns (session)"
    )
    conn.commit()
    return conn


def _insert_pattern(
    conn: sqlite3.Connection,
    *,
    pattern_id: int,
    pattern_name: str,
    file_path: Optional[str],
    line_number: Optional[int],
    description: str,
    auto_fixable: bool,
    fixed: bool,
    session: Optional[str],
    git_sha: Optional[str],
    timestamp: Optional[str] = None,
) -> int:
    """Insert one pattern occurrence and return the new row id."""
    ts = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cur = conn.execute(
        """
        INSERT INTO patterns
            (pattern_id, pattern_name, file_path, line_number, description,
             auto_fixable, fixed, session, git_sha, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            pattern_id,
            pattern_name,
            file_path,
            line_number,
            description,
            int(auto_fixable),
            int(fixed),
            session,
            git_sha,
            ts,
        ),
    )
    conn.commit()
    return cur.lastrowid  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Canonical pattern metadata (pattern_id + auto_fixable flag)
# ---------------------------------------------------------------------------
# Keep in sync with:
#   - CommonIssueFixer.auto_fixable_patterns / manual_review_patterns
#     (scripts/ci/auto_fix_common_issues.py)
#   - generate_json_report pattern_map (same file)

_PATTERN_META: dict[str, dict[str, Any]] = {
    "Unused Imports":          {"id": 1,  "auto_fixable": True},
    "Unused Variables":        {"id": 2,  "auto_fixable": False},
    "YAML Indentation":        {"id": 3,  "auto_fixable": False},
    "Coverage Thresholds":     {"id": 4,  "auto_fixable": True},
    "Tokenizer Fallbacks":     {"id": 5,  "auto_fixable": False},
    "Test Assertions":         {"id": 6,  "auto_fixable": False},
    "Redundant Imports":       {"id": 7,  "auto_fixable": False},
    "CodeQL Alerts":           {"id": 8,  "auto_fixable": False},
    "Unsorted Imports":        {"id": 9,  "auto_fixable": True},
    "Bandit Security":         {"id": 10, "auto_fixable": True},
    "F-String Placeholders":   {"id": 11, "auto_fixable": True},
    "Line Length":             {"id": 12, "auto_fixable": True},
    "W-Series Warnings":       {"id": 13, "auto_fixable": True},
    "Link Checker Config":     {"id": 14, "auto_fixable": True},
    "mypy Baseline Freshness": {"id": 15, "auto_fixable": False},
    "Stub Duplicate Defs":     {"id": 16, "auto_fixable": True},
    "CI SHA Drift":            {"id": 17, "auto_fixable": False},
    "Duplicate Kwargs":        {"id": 18, "auto_fixable": True},
}


# ---------------------------------------------------------------------------
# Ingest from JSON diagnostic report
# ---------------------------------------------------------------------------

def record_from_report(
    report_path: Path,
    conn: sqlite3.Connection,
    session: Optional[str],
    git_sha: Optional[str],
) -> int:
    """Load a JSON diagnostic report produced by ``auto_fix_common_issues.py`` and
    persist every issue it contains into the ``patterns`` table.

    The report JSON structure expected::

        {
            "timestamp": "2026-03-24T18:00:00Z",
            "issues": [
                {
                    "pattern": 18,
                    "pattern_name": "Duplicate Kwargs",
                    "file": "src/foo.py",
                    "line": 42,
                    "message": "Duplicate kwarg 'x' removed",
                    "auto_fix_available": true
                }
            ],
            "fixes_applied": {"Duplicate Kwargs": 1}
        }

    Returns the number of rows inserted (0 on error).
    """
    try:
        data: dict[str, Any] = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read report {report_path}: {exc}", file=sys.stderr)
        return 0

    issues: list[dict[str, Any]] = data.get("issues", [])
    fixes_applied: dict[str, int] = data.get("fixes_applied", {})
    timestamp = data.get("timestamp")

    # Track remaining fix credits per pattern name so that only the first N
    # occurrences of each pattern are marked as fixed (where N is
    # fixes_applied[name]).  This prevents inflating fix_rate when only some
    # occurrences were auto-fixed.
    fix_credits: dict[str, int] = fixes_applied.copy()

    inserted = 0
    for issue in issues:
        name = issue.get("pattern_name", "Unknown")
        pid = issue.get("pattern", 0)
        meta = _PATTERN_META.get(name, {})
        auto_fix = bool(
            meta.get("auto_fixable", issue.get("auto_fix_available", False))
        )
        # Consume one fix credit for this occurrence if any remain.
        if fix_credits.get(name, 0) > 0:
            fixed = True
            fix_credits[name] -= 1
        else:
            fixed = False

        _insert_pattern(
            conn,
            pattern_id=pid or meta.get("id", 0),
            pattern_name=name,
            file_path=issue.get("file"),
            line_number=issue.get("line") or None,
            description=issue.get("message", ""),
            auto_fixable=auto_fix,
            fixed=fixed,
            session=session,
            git_sha=git_sha,
            timestamp=timestamp,
        )
        inserted += 1

    return inserted


# ---------------------------------------------------------------------------
# Query / summary / export helpers
# ---------------------------------------------------------------------------

def query_recent(conn: sqlite3.Connection, limit: int = 20) -> None:
    """Print the most recent pattern occurrences in a compact table."""
    rows = conn.execute(
        "SELECT id, pattern_id, pattern_name, file_path, line_number, "
        "       fixed, session, timestamp "
        "FROM patterns ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    if not rows:
        print("No pattern occurrences recorded yet.")
        return
    print(
        f"{'ID':>4}  {'P#':>3}  {'Name':<25}  {'File':<40}  {'Ln':>5}  "
        f"{'Fx':>3}  Timestamp"
    )
    print("-" * 112)
    for r in rows:
        fp = (r["file_path"] or "")[-40:]
        print(
            f"{r['id']:>4}  {r['pattern_id']:>3}  {r['pattern_name']:<25}  "
            f"{fp:<40}  {(r['line_number'] or 0):>5}  "
            f"{'Y' if r['fixed'] else 'N':>3}  {r['timestamp']}"
        )


def summary(conn: sqlite3.Connection) -> None:
    """Print a frequency summary of all recorded pattern occurrences."""
    rows = conn.execute(
        """
        SELECT pattern_name,
               COUNT(*)       AS total,
               SUM(fixed)     AS fixed_count,
               MAX(timestamp) AS last_seen
        FROM patterns
        GROUP BY pattern_name
        ORDER BY total DESC
        """,
    ).fetchall()
    if not rows:
        print("No pattern occurrences recorded yet.")
        return
    total_all = sum(r["total"] for r in rows)
    fixed_all = sum(r["fixed_count"] for r in rows)
    print(
        f"\nCI Pattern Frequency Summary  "
        f"({total_all} total, {fixed_all} auto-fixed)"
    )
    print(f"{'Pattern':<25}  {'Total':>7}  {'Fixed':>7}  {'Fix%':>6}  Last Seen")
    print("-" * 80)
    for r in rows:
        pct = (r["fixed_count"] / r["total"] * 100) if r["total"] else 0.0
        print(
            f"{r['pattern_name']:<25}  {r['total']:>7}  "
            f"{r['fixed_count']:>7}  {pct:>5.0f}%  {r['last_seen']}"
        )


def high_recurrence(
    conn: sqlite3.Connection, min_occurrences: int = 3, min_fix_rate: float = 0.5
) -> list[dict[str, Any]]:
    """Return patterns whose total occurrences >= *min_occurrences* **and**
    fix-rate >= *min_fix_rate*.

    Used by the pre-commit hook to identify patterns worth warning about.
    """
    rows = conn.execute(
        """
        SELECT pattern_name,
               COUNT(*)   AS total,
               SUM(fixed) AS fixed_count
        FROM patterns
        GROUP BY pattern_name
        HAVING total >= ?
        ORDER BY total DESC
        """,
        (min_occurrences,),
    ).fetchall()
    result = []
    for r in rows:
        fix_rate = (r["fixed_count"] / r["total"]) if r["total"] else 0.0
        if fix_rate >= min_fix_rate:
            result.append(
                {
                    "pattern_name": r["pattern_name"],
                    "total": r["total"],
                    "fixed": r["fixed_count"],
                    "fix_rate": round(fix_rate, 3),
                }
            )
    return result


def cross_pr_correlation(
    conn: sqlite3.Connection,
    min_prs: int = 3,
) -> list[dict[str, Any]]:
    """Return patterns that have recurred across at least *min_prs* distinct PRs.

    A "PR" is identified by a distinct ``git_sha`` value recorded in the
    ``patterns`` table.  Each unique ``git_sha`` represents one CI run
    (commit / PR head), so counting distinct SHAs per pattern gives the number
    of PRs in which that pattern appeared.

    Patterns appearing in fewer than *min_prs* distinct SHAs are excluded.
    Results are ordered by descending ``pr_count``.

    Returns a list of dicts, each with keys:
    - ``pattern_name``   — name of the pattern
    - ``pr_count``       — number of distinct git SHAs (PRs) this pattern appeared in
    - ``total``          — total occurrence count across all PRs
    - ``first_seen_sha`` — the earliest recorded git SHA for this pattern
    - ``last_seen_sha``  — the most recent recorded git SHA for this pattern
    """
    rows = conn.execute(
        """
        SELECT pattern_name,
               COUNT(DISTINCT git_sha)                      AS pr_count,
               COUNT(*)                                     AS total,
               MIN(CASE WHEN git_sha IS NOT NULL THEN git_sha END) AS first_seen_sha,
               MAX(CASE WHEN git_sha IS NOT NULL THEN git_sha END) AS last_seen_sha
        FROM patterns
        WHERE git_sha IS NOT NULL AND git_sha != ''
        GROUP BY pattern_name
        HAVING pr_count >= ?
        ORDER BY pr_count DESC, total DESC
        """,
        (min_prs,),
    ).fetchall()
    return [
        {
            "pattern_name": r["pattern_name"],
            "pr_count": r["pr_count"],
            "total": r["total"],
            "first_seen_sha": r["first_seen_sha"],
            "last_seen_sha": r["last_seen_sha"],
        }
        for r in rows
    ]


def pattern_trend(
    conn: sqlite3.Connection,
    days: int = 7,
) -> list[dict[str, Any]]:
    """Return a 7-day rolling window of daily pattern occurrence counts.

    Each entry in the returned list represents one calendar day (UTC) within
    the last *days* days, with the count of pattern occurrences recorded that
    day.  Days with no occurrences are included with ``count=0`` so the result
    always has exactly *days* entries ordered oldest → newest.

    Used by the ``msv-dashboard`` to render a trend spark-line / bar chart.
    """
    from datetime import timedelta, timezone

    today = datetime.now(timezone.utc).date()
    # Build a date range: [today - (days-1), ..., today] — uses UTC to match SQL DATE('now')
    date_range = [
        (today - timedelta(days=(days - 1 - i))).isoformat() for i in range(days)
    ]

    rows = conn.execute(
        """
        SELECT DATE(timestamp) AS day, COUNT(*) AS cnt
        FROM patterns
        WHERE DATE(timestamp) >= DATE('now', ?)
        GROUP BY day
        ORDER BY day ASC
        """,
        (f"-{days - 1} days",),
    ).fetchall()
    counts: dict[str, int] = {r["day"]: r["cnt"] for r in rows}
    return [{"date": d, "count": counts.get(d, 0)} for d in date_range]


def export_json(conn: sqlite3.Connection, output_path: Optional[Path] = None) -> dict[str, Any]:
    """Serialise the full patterns table (and summary) as a JSON dict.

    If *output_path* is given, also writes the file.  Always returns the dict.
    """
    rows = conn.execute(
        "SELECT id, pattern_id, pattern_name, file_path, line_number, "
        "       auto_fixable, fixed, session, git_sha, timestamp "
        "FROM patterns ORDER BY id ASC"
    ).fetchall()
    data: dict[str, Any] = {
        "exported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": len(rows),
        "occurrences": [dict(r) for r in rows],
    }
    # Add frequency summary
    summary_rows = conn.execute(
        """
        SELECT pattern_name, COUNT(*) AS total, SUM(fixed) AS fixed_count
        FROM patterns GROUP BY pattern_name ORDER BY total DESC
        """
    ).fetchall()
    data["summary"] = [
        {
            "pattern_name": r["pattern_name"],
            "total": r["total"],
            "fixed": r["fixed_count"],
            "fix_rate": round((r["fixed_count"] / r["total"]), 3) if r["total"] else 0.0,
        }
        for r in summary_rows
    ]
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"Exported {len(rows)} occurrences to {output_path}")
    return data


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Record CI pattern occurrences into the cognitive brain SQLite DB "
            "and query the accumulated knowledge graph."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--db",
        default=os.environ.get("CODEX_DB_PATH", _DEFAULT_DB_PATH),
        help=(
            "Path to the SQLite database "
            "(default: $CODEX_DB_PATH or ~/.codex/cli_history.db)"
        ),
    )
    p.add_argument(
        "--session",
        default=(
            os.environ.get("GITHUB_RUN_ID")
            or os.environ.get("COPILOT_SESSION_ID")
        ),
        help="Session / PR identifier for audit trail",
    )
    p.add_argument(
        "--sha",
        default=(
            os.environ.get("CODEX_GIT_SHA")
            or os.environ.get("GITHUB_SHA")
        ),
        help="Git SHA to tag occurrences with",
    )

    sub = p.add_subparsers(dest="cmd")

    # --- record from JSON report ---
    rp = sub.add_parser(
        "record",
        help="Record patterns from a JSON diagnostic report produced by auto_fix_common_issues.py",
    )
    rp.add_argument("--report", required=True, help="Path to JSON diagnostic report")

    # --- insert single occurrence ---
    sp = sub.add_parser("insert", help="Insert a single pattern occurrence")
    sp.add_argument("--pattern-id", type=int, required=True)
    sp.add_argument("--pattern-name", required=True)
    sp.add_argument("--file-path")
    sp.add_argument("--line", type=int)
    sp.add_argument("--description", required=True)
    sp.add_argument("--auto-fixable", action="store_true")
    sp.add_argument("--fixed", action="store_true")

    # --- query ---
    qp = sub.add_parser("query", help="Show recent pattern occurrences")
    qp.add_argument("--limit", type=int, default=20)
    qp.add_argument(
        "--session",
        default=None,
        help="Filter by session identifier (overrides top-level --session)",
    )

    # --- summary ---
    sub.add_parser("summary", help="Show pattern frequency summary")

    # --- high-recurrence ---
    hrp = sub.add_parser(
        "high-recurrence",
        help="List patterns with >= N occurrences and >= R fix-rate (used by pre-commit hook)",
    )
    hrp.add_argument("--min-occurrences", type=int, default=3)
    hrp.add_argument("--min-fix-rate", type=float, default=0.5)
    hrp.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON array instead of table",
    )

    # --- cross-pr correlation ---
    crp = sub.add_parser(
        "cross-pr",
        help="Show patterns that recurred across >= N distinct PRs (git SHAs)",
    )
    crp.add_argument(
        "--min-prs",
        type=int,
        default=3,
        help="Minimum number of distinct PRs (git SHAs) for a pattern to be reported (default: 3)",
    )
    crp.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON array instead of table",
    )

    # --- trend ---
    tp = sub.add_parser(
        "trend",
        help="Show daily pattern occurrence counts for the last N days (7-day rolling window)",
    )
    tp.add_argument("--days", type=int, default=7, help="Number of days to look back (default: 7)")
    tp.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON array instead of table",
    )

    # --- export ---
    ep = sub.add_parser("export", help="Export full knowledge graph as JSON")
    ep.add_argument("--output", help="Output file path (default: stdout)")

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    conn = _open_db(args.db)

    if args.cmd == "record":
        n = record_from_report(Path(args.report), conn, args.session, args.sha)
        print(f"Recorded {n} pattern occurrence(s) from {args.report}")
        return 0 if n >= 0 else 1

    if args.cmd == "insert":
        row_id = _insert_pattern(
            conn,
            pattern_id=args.pattern_id,
            pattern_name=args.pattern_name,
            file_path=args.file_path,
            line_number=args.line,
            description=args.description,
            auto_fixable=args.auto_fixable,
            fixed=args.fixed,
            session=args.session,
            git_sha=args.sha,
        )
        print(f"Inserted pattern occurrence (row id={row_id})")
        return 0

    if args.cmd == "query":
        # Allow query-level session override
        session_filter = getattr(args, "session", None) or None
        if session_filter:
            rows = conn.execute(
                "SELECT id, pattern_id, pattern_name, file_path, line_number, "
                "       fixed, session, timestamp "
                "FROM patterns WHERE session = ? ORDER BY id DESC LIMIT ?",
                (session_filter, args.limit),
            ).fetchall()
            if not rows:
                print(f"No pattern occurrences for session '{session_filter}'.")
            else:
                print(
                    f"{'ID':>4}  {'P#':>3}  {'Name':<25}  {'File':<40}  "
                    f"{'Ln':>5}  {'Fx':>3}  Timestamp"
                )
                print("-" * 112)
                for r in rows:
                    fp = (r["file_path"] or "")[-40:]
                    print(
                        f"{r['id']:>4}  {r['pattern_id']:>3}  "
                        f"{r['pattern_name']:<25}  {fp:<40}  "
                        f"{(r['line_number'] or 0):>5}  "
                        f"{'Y' if r['fixed'] else 'N':>3}  {r['timestamp']}"
                    )
        else:
            query_recent(conn, limit=args.limit)
        return 0

    if args.cmd == "summary":
        summary(conn)
        return 0

    if args.cmd == "high-recurrence":
        results = high_recurrence(
            conn,
            min_occurrences=args.min_occurrences,
            min_fix_rate=args.min_fix_rate,
        )
        if getattr(args, "json", False):
            print(json.dumps(results, indent=2))
        else:
            if not results:
                print(
                    f"No patterns with >= {args.min_occurrences} occurrences "
                    f"and >= {args.min_fix_rate:.0%} fix-rate."
                )
            else:
                print(
                    f"{'Pattern':<25}  {'Total':>7}  {'Fixed':>7}  {'Fix%':>6}"
                )
                print("-" * 55)
                for r in results:
                    print(
                        f"{r['pattern_name']:<25}  {r['total']:>7}  "
                        f"{r['fixed']:>7}  {r['fix_rate']*100:>5.0f}%"
                    )
        return 0

    if args.cmd == "cross-pr":
        results = cross_pr_correlation(conn, min_prs=args.min_prs)
        if getattr(args, "json", False):
            print(json.dumps(results, indent=2))
        else:
            if not results:
                print(
                    f"No patterns found in >= {args.min_prs} distinct PRs."
                )
            else:
                print(
                    f"{'Pattern':<25}  {'PRs':>5}  {'Total':>7}  "
                    f"{'First SHA':<10}  {'Last SHA':<10}"
                )
                print("-" * 70)
                for r in results:
                    first = (r["first_seen_sha"] or "")[:8]
                    last = (r["last_seen_sha"] or "")[:8]
                    print(
                        f"{r['pattern_name']:<25}  {r['pr_count']:>5}  "
                        f"{r['total']:>7}  {first:<10}  {last:<10}"
                    )
        return 0

    if args.cmd == "trend":
        rows = pattern_trend(conn, days=args.days)
        if getattr(args, "json", False):
            print(json.dumps(rows, indent=2))
        else:
            print(f"{'Date':<12}  {'Count':>7}  Chart")
            print("-" * 40)
            max_count = max((r["count"] for r in rows), default=1) or 1
            for r in rows:
                bar = "█" * int(r["count"] / max_count * 20) if r["count"] else ""
                print(f"{r['date']:<12}  {r['count']:>7}  {bar}")
        return 0

    if args.cmd == "export":
        out_path = Path(args.output) if getattr(args, "output", None) else None
        data = export_json(conn, output_path=out_path)
        if out_path is None:
            print(json.dumps(data, indent=2))
        return 0

    # Default (no sub-command): show summary
    summary(conn)
    return 0


if __name__ == "__main__":
    sys.exit(main())
