#!/usr/bin/env python3
"""
Session Metrics Dashboard Generator

Generates a markdown dashboard visualizing session metrics, trends,
and cognitive brain health status.

Usage:
    # Generate dashboard from collected metrics
    python scripts/cognitive/dashboard_generator.py --generate

    # Generate with specific time range
    python scripts/cognitive/dashboard_generator.py --hours 48

    # Save to specific location
    python scripts/cognitive/dashboard_generator.py --output .codex/cognitive_brain/dashboard.md
"""

import argparse
import json
import logging
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


def load_metrics(metrics_path: Path) -> Optional[dict[str, Any]]:
    """Load metrics from JSON file."""
    if not metrics_path.exists():
        return None
    try:
        with open(metrics_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None


def generate_progress_bar(
    value: float,
    max_value: float = 1.0,
    width: int = 20,
    filled: str = "█",
    empty: str = "░"
) -> str:
    """Generate a progress bar string."""
    if max_value <= 0:
        return empty * width

    ratio = min(1.0, value / max_value)
    filled_count = int(ratio * width)
    return filled * filled_count + empty * (width - filled_count)


def generate_trend_indicator(trend: str) -> str:
    """Generate a trend indicator emoji."""
    indicators = {
        "increasing": "📈",
        "decreasing": "📉",
        "stable": "➡️",
        "excellent": "🌟",
        "good": "✅",
        "fair": "⚠️",
        "needs_attention": "🔴"
    }
    return indicators.get(trend, "❓")


def generate_ascii_chart(
    data: list[tuple[str, float]],
    width: int = 30,
    title: str = ""
) -> str:
    """Generate an ASCII bar chart."""
    if not data:
        return "(No data available)"

    lines = []
    if title:
        lines.append(f"**{title}**")
        lines.append("```")

    max_val = max(v for _, v in data) if data else 1

    for label, value in data:
        bar_len = int((value / max_val) * width) if max_val > 0 else 0
        bar = "█" * bar_len
        lines.append(f"{label:15} {bar} {value:.0f}")

    if title:
        lines.append("```")

    return "\n".join(lines)


def generate_sparkline(values: list[float], width: int = 10) -> str:
    """Generate a simple sparkline from values."""
    if not values:
        return "▁" * width

    if len(values) < width:
        # Pad with first value
        values = [values[0]] * (width - len(values)) + values
    elif len(values) > width:
        # Take last N values
        values = values[-width:]

    min_val = min(values)
    max_val = max(values)
    range_val = max_val - min_val if max_val != min_val else 1

    chars = "▁▂▃▄▅▆▇█"

    sparkline = ""
    for v in values:
        idx = int(((v - min_val) / range_val) * (len(chars) - 1))
        sparkline += chars[idx]

    return sparkline


def format_duration(minutes: float) -> str:
    """Format duration in a human-readable way."""
    if minutes < 60:
        return f"{minutes:.0f}m"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:.0f}h {mins:.0f}m"


def _generate_ci_pattern_trend_section(days: int = 7) -> str:
    """Generate a 7-day rolling CI pattern trend bar chart for the dashboard.

    Queries the cognitive brain SQLite DB via ``pattern_recorder.pattern_trend()``.
    Returns a markdown-formatted ASCII bar chart.  Fails gracefully (returns a
    placeholder message) when the DB is absent or the import fails.
    """
    try:
        import os
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "ci"))
        import pattern_recorder as pr  # noqa: PLC0415

        db_path = os.environ.get(
            "CODEX_DB_PATH",
            os.path.expanduser("~/.codex/cli_history.db"),
        )
        conn = pr._open_db(db_path)
        try:
            rows = pr.pattern_trend(conn, days=days)
        finally:
            conn.close()
    except Exception:
        return "_CI pattern DB unavailable — run `pattern_recorder.py trend` to populate._"

    if not any(r["count"] for r in rows):
        return "_No CI pattern occurrences recorded in the last 7 days._"

    max_count = max(r["count"] for r in rows) or 1
    bar_width = 20
    chars = "▁▂▃▄▅▆▇█"
    lines = ["```"]
    for r in rows:
        ratio = r["count"] / max_count
        bar = "█" * int(ratio * bar_width)
        spark_idx = int(ratio * (len(chars) - 1))
        spark = chars[spark_idx] if r["count"] > 0 else " "
        lines.append(f"{r['date']}  {spark} {bar:<{bar_width}}  {r['count']:>3}")
    lines.append("```")
    return "\n".join(lines)


def generate_dashboard(
    metrics: dict[str, Any],
    include_charts: bool = True
) -> str:
    """Generate the markdown dashboard."""
    now = datetime.now(timezone.utc)

    # Extract data
    period = metrics.get("period", {})
    files = metrics.get("files", {})
    patterns = metrics.get("patterns", {})
    commits = metrics.get("commits", {})
    sessions = metrics.get("sessions", {})
    trends = metrics.get("trends", {})
    # quality metrics used for future enhancements

    # Calculate derived values
    duration = period.get("duration_minutes", 0)
    total_files = files.get("total_operations", 0)
    pattern_success = patterns.get("avg_success_rate", 0)
    total_commits = commits.get("total", 0)

    # Generate health score
    health_score = calculate_health_score(metrics)
    health_status = get_health_status(health_score)

    dashboard = f"""# 🧠 Cognitive Brain Dashboard

> **Generated:** {now.strftime("%Y-%m-%d %H:%M:%S UTC")}
> **Period:** {format_duration(duration)}
> **Health:** {health_status["emoji"]} {health_status["label"]} ({health_score:.0f}%)

---

## 📊 Quick Stats

| Metric | Value | Trend |
|--------|-------|-------|
| Sessions | {sessions.get("total", 0)} | {generate_trend_indicator(trends.get("overall_health", "stable"))} |
| Files Changed | {total_files} | {generate_trend_indicator(trends.get("files_trend", "stable"))} |
| Commits | {total_commits} | {generate_trend_indicator(trends.get("commits_trend", "stable"))} |
| Pattern Success | {pattern_success:.1%} | {generate_trend_indicator(trends.get("patterns_trend", "stable"))} |

---

## 📈 Health Score

```
{generate_progress_bar(health_score, 100, 40)} {health_score:.0f}%
```

| Component | Score | Status |
|-----------|-------|--------|
| File Operations | {min(100, total_files * 5):.0f}% | {generate_progress_bar(min(100, total_files * 5), 100, 15)} |
| Pattern Usage | {pattern_success * 100:.0f}% | {generate_progress_bar(pattern_success * 100, 100, 15)} |
| Commit Activity | {min(100, total_commits * 10):.0f}% | {generate_progress_bar(min(100, total_commits * 10), 100, 15)} |

---

## 📁 File Activity

| Type | Count |
|------|-------|
| Created | {files.get("created", 0)} |
| Modified | {files.get("modified", 0)} |
| Total Operations | {total_files} |

"""

    if include_charts:
        file_data = [
            ("Created", files.get("created", 0)),
            ("Modified", files.get("modified", 0))
        ]
        dashboard += generate_ascii_chart(file_data, title="File Operations")
        dashboard += "\n\n"

    dashboard += f"""---

## 🧩 Pattern Analysis

| Metric | Value |
|--------|-------|
| Patterns Applied | {patterns.get("applied", 0)} |
| Patterns Learned | {patterns.get("learned", 0)} |
| Unique Patterns | {len(patterns.get("unique_patterns", []))} |
| Avg Success Rate | {pattern_success:.1%} |

"""

    unique_patterns = patterns.get("unique_patterns", [])
    if unique_patterns:
        dashboard += "### Active Patterns\n"
        for p in unique_patterns[:8]:
            dashboard += f"- `{p}`\n"
        if len(unique_patterns) > 8:
            dashboard += f"- ... and {len(unique_patterns) - 8} more\n"
        dashboard += "\n"

    dashboard += f"""---

## 📝 Commit Activity

| Metric | Value |
|--------|-------|
| Total Commits | {total_commits} |
| By Copilot | {commits.get("by_copilot", 0)} |

---

## 🔁 CI Pattern Trend (7-Day Rolling Window)

{_generate_ci_pattern_trend_section()}

---

## 🎯 Period Summary

- **Start:** {period.get("start", "N/A")}
- **End:** {period.get("end", "N/A")}
- **Duration:** {format_duration(duration)}

---

## 📋 Trends

| Trend | Status |
|-------|--------|
| Files | {generate_trend_indicator(trends.get("files_trend", "stable"))} {trends.get("files_trend", "stable")} |
| Patterns | {generate_trend_indicator(trends.get("patterns_trend", "stable"))} {trends.get("patterns_trend", "stable")} |
| Commits | {generate_trend_indicator(trends.get("commits_trend", "stable"))} {trends.get("commits_trend", "stable")} |
| Overall Health | {generate_trend_indicator(trends.get("overall_health", "good"))} {trends.get("overall_health", "good")} |

---

## 🔗 Related Resources

- Pattern Store: `.codex/cognitive_brain/pattern_learning_store.json`
- Objectives: `.codex/cognitive_brain/objectives_tracker.md`
- Action Log: `.codex/action_log.ndjson`
- Session Tracker: `.codex/cognitive_brain/session_tracker.md`

---

## 🔄 Refresh Dashboard

```bash
# Regenerate dashboard
python scripts/cognitive/dashboard_generator.py --generate

# With custom time range
python scripts/cognitive/dashboard_generator.py --hours 48
```

---

**Dashboard Version:** 1.0.0
**Last Updated:** {now.isoformat()}
"""

    return dashboard


def calculate_health_score(metrics: dict[str, Any]) -> float:
    """Calculate overall health score (0-100)."""
    scores = []

    # File activity score (0-25)
    files = metrics.get("files", {})
    file_ops = files.get("total_operations", 0)
    file_score = min(25, file_ops * 2)
    scores.append(file_score)

    # Pattern success score (0-25)
    patterns = metrics.get("patterns", {})
    pattern_rate = patterns.get("avg_success_rate", 0)
    pattern_score = pattern_rate * 25
    scores.append(pattern_score)

    # Commit activity score (0-25)
    commits = metrics.get("commits", {})
    commit_count = commits.get("total", 0)
    commit_score = min(25, commit_count * 5)
    scores.append(commit_score)

    # Session activity score (0-25)
    sessions = metrics.get("sessions", {})
    session_count = sessions.get("total", 0)
    session_score = min(25, session_count * 10)
    scores.append(session_score)

    return sum(scores)


def get_health_status(score: float) -> dict[str, str]:
    """Get health status based on score."""
    if score >= 90:
        return {"emoji": "🌟", "label": "Excellent", "color": "green"}
    if score >= 70:
        return {"emoji": "✅", "label": "Good", "color": "green"}
    if score >= 50:
        return {"emoji": "⚠️", "label": "Fair", "color": "yellow"}
    if score >= 30:
        return {"emoji": "🔶", "label": "Needs Attention", "color": "orange"}
    return {"emoji": "🔴", "label": "Critical", "color": "red"}


def save_dashboard(
    dashboard: str,
    output_path: Path
) -> None:
    """Save dashboard to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(dashboard)
    logger.info(f"Saved dashboard to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Session Metrics Dashboard Generator"
    )
    parser.add_argument(
        '--generate',
        action='store_true',
        help="Generate the dashboard"
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help="Time range in hours (default: 24)"
    )
    parser.add_argument(
        '--metrics-file',
        type=str,
        help="Load metrics from specific file instead of collecting"
    )
    parser.add_argument(
        '--output',
        type=str,
        help="Output file path"
    )
    parser.add_argument(
        '--no-charts',
        action='store_true',
        help="Disable ASCII charts"
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help="Suppress output"
    )

    args = parser.parse_args()

    if not args.generate and not args.metrics_file:
        parser.print_help()
        return

    repo_root = get_repo_root()

    # Load or collect metrics
    if args.metrics_file:
        metrics = load_metrics(Path(args.metrics_file))
        if not metrics:
            logger.error(f"Could not load metrics from: {args.metrics_file}")
            return
    else:
        # Import and use metrics collector
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from metrics_collector import (
            calculate_trends,
            extract_session_metrics,
            get_git_commits,
            load_action_log,
            load_pattern_store,
        )

        since = datetime.now(timezone.utc) - timedelta(hours=args.hours)

        action_log_path = repo_root / '.codex' / 'action_log.ndjson'
        pattern_store_path = repo_root / '.codex' / 'cognitive_brain' / 'pattern_learning_store.json'

        action_entries = load_action_log(action_log_path, since=since)
        pattern_store = load_pattern_store(pattern_store_path)
        commits = get_git_commits(repo_root, since=since)

        metrics = extract_session_metrics(action_entries, pattern_store, commits)
        metrics["trends"] = calculate_trends(metrics)

    # Generate dashboard
    dashboard = generate_dashboard(metrics, include_charts=not args.no_charts)

    # Output
    if args.output:
        save_dashboard(dashboard, Path(args.output))
    elif not args.quiet:
        print(dashboard)

    # Also save to default location if generating
    if args.generate and not args.output:
        default_path = repo_root / '.codex' / 'cognitive_brain' / 'dashboard.md'
        save_dashboard(dashboard, default_path)


if __name__ == "__main__":
    main()
