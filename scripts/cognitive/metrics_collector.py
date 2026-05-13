#!/usr/bin/env python3
"""
Session Metrics Collector

Collects and aggregates metrics from Copilot Coding Agent sessions for
the cognitive brain dashboard. Extracts data from:
- action_log.ndjson (file operations)
- pattern_learning_store.json (patterns)
- objectives_tracker.md (objectives)
- Git history (commits)

Usage:
    # Collect metrics for last 24 hours
    python scripts/cognitive/metrics_collector.py --hours 24

    # Collect for specific session
    python scripts/cognitive/metrics_collector.py --session-id "my-session"

    # Export to JSON
    python scripts/cognitive/metrics_collector.py --export metrics.json
"""

import argparse
import json
import logging
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_repo_root() -> Path:
    """Get the repository root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / '.git').exists():
            return current
        current = current.parent
    return Path.cwd()


def parse_timestamp(ts: str) -> Optional[datetime]:
    """Parse an ISO format timestamp."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return None


def load_action_log(
    log_path: Path,
    since: Optional[datetime] = None
) -> list[dict[str, Any]]:
    """Load action log entries."""
    if not log_path.exists():
        return []

    entries = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if since and 'timestamp' in entry:
                    entry_time = parse_timestamp(entry['timestamp'])
                    if entry_time and entry_time < since:
                        continue
                entries.append(entry)
            except json.JSONDecodeError:
                continue

    return entries


def load_pattern_store(store_path: Path) -> dict[str, Any]:
    """Load pattern learning store."""
    if not store_path.exists():
        return {"patterns": {}, "statistics": {}, "learning_log": []}

    try:
        with open(store_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"patterns": {}, "statistics": {}, "learning_log": []}


def get_git_commits(
    repo_root: Path,
    since: Optional[datetime] = None,
    limit: int = 100
) -> list[dict[str, Any]]:
    """Get git commit history."""
    try:
        cmd = ['git', '--no-pager', 'log', f'-{limit}', '--format=%H|%s|%ai']
        if since:
            cmd.extend(['--since', since.isoformat()])

        result = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True
        )

        commits = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                parts = line.split('|', 2)
                if len(parts) >= 3:
                    commits.append({
                        'sha': parts[0][:8],
                        'message': parts[1],
                        'date': parts[2]
                    })
        return commits
    except Exception as e:
        logger.warning(f"Could not get git commits: {e}")
        return []


def extract_session_metrics(
    action_entries: list[dict[str, Any]],
    pattern_store: dict[str, Any],
    commits: list[dict[str, Any]]
) -> dict[str, Any]:
    """Extract comprehensive session metrics."""
    now = datetime.now(timezone.utc)

    # Initialize metrics
    metrics = {
        "collected_at": now.isoformat(),
        "period": {
            "start": None,
            "end": now.isoformat(),
            "duration_minutes": 0
        },
        "sessions": {
            "total": 0,
            "completed": 0,
            "in_progress": 0
        },
        "tasks": {
            "completed": 0,
            "pending": 0,
            "completion_rate": 0.0
        },
        "files": {
            "created": 0,
            "modified": 0,
            "deleted": 0,
            "total_operations": 0
        },
        "patterns": {
            "applied": 0,
            "learned": 0,
            "unique_patterns": [],
            "avg_success_rate": 0.0
        },
        "commits": {
            "total": len(commits),
            "by_copilot": 0
        },
        "quality": {
            "tests_passed": 0,
            "tests_failed": 0,
            "lint_errors": 0
        }
    }

    # Track unique items
    files_created = set()
    files_modified = set()
    patterns_used = set()
    sessions_seen = set()

    # Process action entries
    first_timestamp = None
    for entry in action_entries:
        ts = parse_timestamp(entry.get('timestamp', ''))
        if ts and (first_timestamp is None or ts < first_timestamp):
            first_timestamp = ts

        action = entry.get('action', '').lower()
        path = entry.get('path', '')
        session = entry.get('session_id', '')

        if session:
            sessions_seen.add(session)

        if action in ('create', 'created'):
            files_created.add(path)
        elif action in ('edit', 'edited', 'update', 'updated', 'modify', 'modified'):
            files_modified.add(path)

    # Update file metrics
    metrics["files"]["created"] = len(files_created)
    metrics["files"]["modified"] = len(files_modified)
    metrics["files"]["total_operations"] = len(files_created) + len(files_modified)

    # Update session metrics
    metrics["sessions"]["total"] = max(1, len(sessions_seen))

    # Update period
    if first_timestamp:
        metrics["period"]["start"] = first_timestamp.isoformat()
        duration = now - first_timestamp
        metrics["period"]["duration_minutes"] = round(duration.total_seconds() / 60, 2)

    # Process pattern store
    patterns = pattern_store.get("patterns", {})
    learning_log = pattern_store.get("learning_log", [])

    for pattern_id, _ in patterns.items():
        patterns_used.add(pattern_id)

    for log_entry in learning_log:
        applied = log_entry.get("patterns_applied", [])
        learned = log_entry.get("patterns_learned", [])
        metrics["patterns"]["applied"] += len(applied)
        metrics["patterns"]["learned"] += len(learned)
        patterns_used.update(applied)
        patterns_used.update(learned)

    metrics["patterns"]["unique_patterns"] = list(patterns_used)

    # Calculate average pattern success rate
    if patterns:
        success_rates = [
            p.get("success_rate", 0.5)
            for p in patterns.values()
            if isinstance(p.get("success_rate"), (int, float))
        ]
        if success_rates:
            metrics["patterns"]["avg_success_rate"] = round(
                sum(success_rates) / len(success_rates), 3
            )

    # Count Copilot commits (using Co-authored-by trailer)
    for commit in commits:
        msg = commit.get('message', '').lower()
        # Only match actual Copilot co-author signature, not general patterns
        if 'co-authored-by:' in msg and ('copilot' in msg or 'github' in msg):
            metrics["commits"]["by_copilot"] += 1

    return metrics


def calculate_trends(
    current: dict[str, Any],
    previous: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """Calculate metric trends compared to previous period."""
    trends = {
        "files_trend": "stable",
        "patterns_trend": "stable",
        "commits_trend": "stable",
        "overall_health": "good"
    }

    if not previous:
        return trends

    # Compare file operations
    curr_files = current.get("files", {}).get("total_operations", 0)
    prev_files = previous.get("files", {}).get("total_operations", 0)
    if prev_files > 0:
        change = (curr_files - prev_files) / prev_files
        if change > 0.1:
            trends["files_trend"] = "increasing"
        elif change < -0.1:
            trends["files_trend"] = "decreasing"

    # Compare pattern usage
    curr_patterns = current.get("patterns", {}).get("applied", 0)
    prev_patterns = previous.get("patterns", {}).get("applied", 0)
    if prev_patterns > 0:
        change = (curr_patterns - prev_patterns) / prev_patterns
        if change > 0.1:
            trends["patterns_trend"] = "increasing"
        elif change < -0.1:
            trends["patterns_trend"] = "decreasing"

    # Overall health assessment
    success_rate = current.get("patterns", {}).get("avg_success_rate", 0)
    if success_rate >= 0.9:
        trends["overall_health"] = "excellent"
    elif success_rate >= 0.7:
        trends["overall_health"] = "good"
    elif success_rate >= 0.5:
        trends["overall_health"] = "fair"
    else:
        trends["overall_health"] = "needs_attention"

    return trends


def generate_ascii_chart(
    data: list[tuple[str, float]],
    width: int = 40,
    title: str = "Chart"
) -> str:
    """Generate a simple ASCII bar chart."""
    if not data:
        return f"{title}\n(No data available)"

    lines = [title, "=" * len(title)]

    max_val = max(v for _, v in data) if data else 1

    for label, value in data:
        bar_len = int((value / max_val) * width) if max_val > 0 else 0
        bar = "█" * bar_len + "░" * (width - bar_len)
        lines.append(f"{label:12} │{bar}│ {value:.1f}")

    return "\n".join(lines)


def save_metrics(
    metrics: dict[str, Any],
    output_path: Path
) -> None:
    """Save metrics to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Saved metrics to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Session Metrics Collector"
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help="Collect metrics for last N hours (default: 24)"
    )
    parser.add_argument(
        '--session-id',
        type=str,
        help="Collect metrics for specific session"
    )
    parser.add_argument(
        '--export',
        type=str,
        help="Export metrics to JSON file"
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help="Suppress output"
    )

    args = parser.parse_args()

    repo_root = get_repo_root()

    # Determine time range
    since = datetime.now(timezone.utc) - timedelta(hours=args.hours)

    # Load data sources
    action_log_path = repo_root / '.codex' / 'action_log.ndjson'
    pattern_store_path = repo_root / '.codex' / 'cognitive_brain' / 'pattern_learning_store.json'

    action_entries = load_action_log(action_log_path, since=since)
    pattern_store = load_pattern_store(pattern_store_path)
    commits = get_git_commits(repo_root, since=since)

    # Extract metrics
    metrics = extract_session_metrics(action_entries, pattern_store, commits)
    metrics["trends"] = calculate_trends(metrics)

    # Export if requested
    if args.export:
        save_metrics(metrics, Path(args.export))

    # Output
    if not args.quiet:
        print(json.dumps(metrics, indent=2))

    return metrics


if __name__ == "__main__":
    main()
