#!/usr/bin/env python3
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List


def parse_ts_from_name(path: Path) -> datetime | None:
    try:
        ts_part = path.stem.split("_", 1)[1]
        dt = datetime.strptime(ts_part, "%Y%m%dT%H%M%SZ")
        return dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def prune_older_than(directory: Path, keep_days: int) -> List[str]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=keep_days)
    removed: List[str] = []
    for path in sorted(directory.glob("ratelimit_*.json")):
        ts = parse_ts_from_name(path)
        if ts and ts < cutoff:
            path.unlink(missing_ok=True)
            removed.append(path.name)
    return removed


def main(argv: List[str] | None = None) -> int:
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
