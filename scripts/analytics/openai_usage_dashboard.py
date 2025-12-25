"""
OpenAI Usage Dashboard.

Visualizes API usage, costs, and model performance from audit logs.

Author: Copilot Agent
Generated: 2025-12-24

Safeguards:
- Input validation on log files
- Bounds checking on data sizes
- Defensive error handling
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards: Bounds
MAX_LOG_ENTRIES = 100000
MAX_REPORT_DAYS = 365


def load_audit_logs(log_path: Path) -> list[dict[str, Any]]:
    """Load audit logs from JSONL file."""
    if not log_path.exists():
        logger.warning("Audit log not found: %s", log_path)
        return []

    entries: list[dict[str, Any]] = []

    try:
        with open(log_path) as f:
            for i, line in enumerate(f):
                if i >= MAX_LOG_ENTRIES:
                    logger.warning(f"Truncated at {MAX_LOG_ENTRIES} entries")
                    break
                try:
                    entries.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        logger.error("Error loading audit logs: %s", e)
        return []

    logger.info(f"Loaded {len(entries)} audit log entries")
    return entries


def calculate_usage_stats(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate usage statistics from audit log entries."""
    if not entries:
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "models_used": [],
            "avg_duration_ms": 0,
            "cost_by_model": {},
            "requests_by_model": {},
            "daily_usage": {},
        }

    stats: dict[str, Any] = {
        "total_requests": len(entries),
        "successful_requests": sum(1 for e in entries if e.get("success", False)),
        "total_tokens": sum(e.get("tokens_used", 0) for e in entries),
        "total_cost": sum(e.get("estimated_cost", 0.0) for e in entries),
        "models_used": list(set(e.get("model", "unknown") for e in entries)),
        "avg_duration_ms": 0,
        "cost_by_model": {},
        "requests_by_model": {},
        "daily_usage": {},
    }

    # Calculate averages
    durations = [e.get("duration_ms", 0) for e in entries if e.get("duration_ms")]
    if durations:
        stats["avg_duration_ms"] = sum(durations) // len(durations)

    # Model breakdown
    for entry in entries:
        model = entry.get("model", "unknown")

        # Cost by model
        if model not in stats["cost_by_model"]:
            stats["cost_by_model"][model] = 0.0
        stats["cost_by_model"][model] += entry.get("estimated_cost", 0.0)

        # Requests by model
        if model not in stats["requests_by_model"]:
            stats["requests_by_model"][model] = 0
        stats["requests_by_model"][model] += 1

        # Daily usage
        timestamp = entry.get("timestamp", "")
        if timestamp:
            try:
                date_str = timestamp[:10]  # Extract YYYY-MM-DD
                if date_str not in stats["daily_usage"]:
                    stats["daily_usage"][date_str] = {
                        "requests": 0,
                        "cost": 0.0,
                        "tokens": 0,
                    }
                stats["daily_usage"][date_str]["requests"] += 1
                daily = stats["daily_usage"][date_str]
                daily["cost"] += entry.get("estimated_cost", 0.0)
                daily["tokens"] += entry.get("tokens_used", 0)
            except (ValueError, IndexError) as exc:
                logger.warning(
                    "Skipping entry with invalid timestamp %r: %s",
                    timestamp,
                    exc,
                )

    return stats


def generate_markdown_dashboard(stats: dict[str, Any]) -> str:
    """Generate markdown dashboard from usage statistics."""
    timestamp = datetime.now(timezone.utc).isoformat()

    total = stats["total_requests"]
    success = stats["successful_requests"]
    success_rate = (success / max(total, 1)) * 100

    dashboard = f"""# OpenAI Usage Dashboard

> Generated: {timestamp}

## Summary

| Metric | Value |
|--------|-------|
| **Total Requests** | {total:,} |
| **Successful Requests** | {success:,} |
| **Success Rate** | {success_rate:.1f}% |
| **Total Tokens** | {stats['total_tokens']:,} |
| **Total Cost** | ${stats['total_cost']:.4f} |
| **Avg Response Time** | {stats['avg_duration_ms']:,}ms |

## Model Usage

| Model | Requests | Cost | Avg Cost/Request |
|-------|----------|------|------------------|
"""

    for model in stats.get("models_used", []):
        requests = stats["requests_by_model"].get(model, 0)
        cost = stats["cost_by_model"].get(model, 0.0)
        avg_cost = cost / max(requests, 1)
        dashboard += f"| `{model}` | {requests:,} | ${cost:.4f} | ${avg_cost:.6f} |\n"

    dashboard += """
## Daily Trends

| Date | Requests | Tokens | Cost |
|------|----------|--------|------|
"""

    # Sort by date descending, show last 14 days
    daily = sorted(stats.get("daily_usage", {}).items(), reverse=True)[:14]
    for date_str, usage in daily:
        req = usage["requests"]
        tok = usage["tokens"]
        cst = usage["cost"]
        dashboard += f"| {date_str} | {req:,} | {tok:,} | ${cst:.4f} |\n"

    dashboard += """
## Cost Optimization Tips

1. **Use `gpt-4o-mini`** for simple tasks (90% cheaper than gpt-4)
2. **Cache common prompts** to reduce token usage
3. **Batch requests** when possible
4. **Monitor reasoning model usage** (o1, o3) - higher cost per request

## Audit Log Location

Logs are stored in `.github/audit/openai_usage.jsonl`

---

*Dashboard auto-generated by `scripts/analytics/openai_usage_dashboard.py`*
"""

    return dashboard


def generate_dashboard(
    log_path: Path | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Generate usage dashboard from audit logs."""
    if log_path is None:
        log_path = Path(".github/audit/openai_usage.jsonl")

    if output_path is None:
        output_path = Path(".github/audit/usage_dashboard.md")

    # Load logs
    entries = load_audit_logs(log_path)

    # Calculate stats
    stats = calculate_usage_stats(entries)

    # Generate dashboard
    dashboard = generate_markdown_dashboard(stats)

    # Save dashboard
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(dashboard)

    logger.info(f"✅ Dashboard saved to {output_path}")

    return stats


def main() -> None:
    """Main entry point."""
    logging.basicConfig(level=logging.INFO)

    stats = generate_dashboard()

    # Print summary
    print("\n📊 OpenAI Usage Summary")
    print(f"  Total Requests: {stats['total_requests']:,}")
    print(f"  Total Cost: ${stats['total_cost']:.4f}")
    print(f"  Models Used: {', '.join(stats['models_used']) or 'None'}")

    if not stats["total_requests"]:
        print("\n💡 No usage data yet. " "Run the autonomous agent to generate usage logs.")


if __name__ == "__main__":
    main()
