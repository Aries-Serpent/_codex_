#!/usr/bin/env python3
"""
Store Performance Analytics
Phase 4D Planset 007 - Historical analytics storage

Stores performance metrics in:
- JSON time-series database (.codex/perf/analytics.json)
- Compressed historical archive (4+ weeks trending)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


def load_analytics(path: Path) -> dict[str, Any]:
    """Load existing analytics"""
    if not path.exists():
        return {"entries": []}
    
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load analytics: {e}", file=sys.stderr)
        return {"entries": []}


def save_analytics(path: Path, data: dict[str, Any]) -> None:
    """Save analytics to file"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def prune_old_entries(data: dict[str, Any], max_days: int = 28) -> None:
    """Remove entries older than max_days"""
    cutoff = datetime.now() - timedelta(days=max_days)
    
    entries = data.get("entries", [])
    original_count = len(entries)
    
    # Filter out old entries
    data["entries"] = [
        e for e in entries
        if datetime.fromisoformat(e.get("timestamp", "")) >= cutoff
    ]
    
    pruned_count = original_count - len(data["entries"])
    if pruned_count > 0:
        print(f"Pruned {pruned_count} entries older than {max_days} days")


def main() -> int:
    """Store performance analytics"""
    parser = argparse.ArgumentParser(
        description="Store performance analytics"
    )
    parser.add_argument(
        "--metrics",
        type=Path,
        required=True,
        help="Metrics JSON file to store",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        required=True,
        help="GitHub Actions run ID",
    )
    parser.add_argument(
        "--commit",
        type=str,
        required=True,
        help="Commit SHA",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".codex/perf/analytics.json"),
        help="Output analytics file",
    )
    
    args = parser.parse_args()
    
    # Load current metrics
    if not args.metrics.exists():
        print(f"Error: Metrics file not found: {args.metrics}", file=sys.stderr)
        return 1
    
    with open(args.metrics, "r") as f:
        metrics = json.load(f)
    
    # Load existing analytics
    analytics = load_analytics(args.output)
    
    # Create new entry
    entry = {
        "timestamp": datetime.now().isoformat(),
        "run_id": args.run_id,
        "commit": args.commit,
        "metrics": metrics,
    }
    
    # Add to analytics
    if "entries" not in analytics:
        analytics["entries"] = []
    analytics["entries"].append(entry)
    
    # Prune old entries (keep 4 weeks)
    prune_old_entries(analytics, max_days=28)
    
    # Update metadata
    analytics["last_updated"] = datetime.now().isoformat()
    analytics["total_entries"] = len(analytics["entries"])
    
    # Save analytics
    save_analytics(args.output, analytics)
    
    print(f"✅ Analytics stored: {len(analytics['entries'])} entries in database")
    return 0


if __name__ == "__main__":
    sys.exit(main())
