#!/usr/bin/env python3
"""
Prune Rate Limit History

Purpose:
    Runs prune_rate_limit_history

Usage:
    python scripts/connectors/prune_rate_limit_history.py [options]
    
    Examples:
    $ python scripts/connectors/prune_rate_limit_history.py --help

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
import logging
logger = logging.getLogger(__name__)

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path


def parse_ts_from_name(path: Path) -> datetime | None:
    try:
        ts_part = path.stem.split("_", 1)[1]
        dt = datetime.strptime(ts_part, "%Y%m%dT%H%M%SZ")
        return dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def prune_older_than(directory: Path, keep_days: int) -> list[str]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=keep_days)
    removed: list[str] = []
    for path in sorted(directory.glob("ratelimit_*.json")):
        ts = parse_ts_from_name(path)
        if ts and ts < cutoff:
            path.unlink(missing_ok=True)
            removed.append(path.name)
    return removed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prune rate-limit history JSON files older than the configured window"
    )
    parser.add_argument("--root", default="connectors/history")
    parser.add_argument("--days", type=int, default=90)
    args = parser.parse_args(argv)

    root = Path(args.root)
    if not root.exists():
        print("[OK] Nothing to prune")
        return 0

    removed = prune_older_than(root, args.days)
    print(f"[OK] Pruned {len(removed)} file(s) older than {args.days} days")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
