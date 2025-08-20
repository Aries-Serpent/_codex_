#!/usr/bin/env python3
"""Summarize errors logged in `.codex/errors.ndjson`.

The script groups error entries by their message and assigns each
unique message a stable identifier derived from the message content.
It supports filtering by timestamp and selecting only unanswered
errors.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

DEFAULT_LOG_PATH = Path(".codex/errors.ndjson")


def parse_ts(ts: str) -> datetime:
    """Parse an ISO 8601 timestamp, accepting a trailing ``Z``."""
    if ts.endswith("Z"):
        ts = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(ts)


def load_entries(path: Path) -> List[dict]:
    """Load NDJSON entries from ``path``.

    Malformed lines are ignored.
    """
    entries: List[dict] = []
    if not path.exists():
        return entries
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def group_errors(
    entries: Iterable[dict],
    since: Optional[datetime] = None,
    unanswered_only: bool = False,
) -> List[Dict[str, object]]:
    """Group error entries by message.

    Parameters
    ----------
    entries:
        Iterable of error records.
    since:
        If provided, only entries with ``ts`` greater than or equal to this
        timestamp are considered.
    unanswered_only:
        When ``True``, exclude groups containing any ``answer_id`` field.
    """
    grouped: Dict[str, List[dict]] = {}
    for entry in entries:
        ts_str = entry.get("ts")
        if since and ts_str:
            try:
                if parse_ts(ts_str) < since:
                    continue
            except Exception:
                continue
        message = entry.get("error")
        if not message:
            continue
        grouped.setdefault(message, []).append(entry)

    results: List[Dict[str, object]] = []
    for message, items in grouped.items():
        if unanswered_only and any("answer_id" in item for item in items):
            continue
        uid = hashlib.sha256(message.encode("utf-8")).hexdigest()[:8]
        results.append({"id": uid, "message": message, "count": len(items)})

    results.sort(key=lambda r: r["message"])  # deterministic output
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize errors from .codex/errors.ndjson"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=DEFAULT_LOG_PATH,
        help="Path to errors.ndjson (default: .codex/errors.ndjson)",
    )
    parser.add_argument(
        "--since",
        help="ISO timestamp; only include entries with ts >= since",
    )
    parser.add_argument(
        "--unanswered-only",
        action="store_true",
        help="Exclude groups that contain an answer_id",
    )
    args = parser.parse_args()

    since_dt = parse_ts(args.since) if args.since else None
    entries = load_entries(Path(args.path))
    summaries = group_errors(entries, since=since_dt, unanswered_only=args.unanswered_only)
    for rec in summaries:
        print(f"{rec['id']}\t{rec['count']}\t{rec['message']}")


if __name__ == "__main__":
    main()
