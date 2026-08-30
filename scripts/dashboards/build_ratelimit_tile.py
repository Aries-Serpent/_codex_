#!/usr/bin/env python3
"""
Build Ratelimit Tile

Purpose:
    Builds ratelimit_tile

Usage:
    python scripts/dashboards/build_ratelimit_tile.py [options]

    Examples:
    $ python scripts/dashboards/build_ratelimit_tile.py --help

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
import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


@dataclass
class RateLimitEntry:
    captured: datetime
    resources: dict[str, dict[str, int]]

    def as_series_point(self, key: str) -> tuple[str, int] | None:
        resource = self.resources.get(key) or {}
        remaining = resource.get("remaining")
        if remaining is None:
            return None
        value = int(remaining)
        return (self.captured.strftime(ISO_FORMAT), value)


def parse_timestamp(raw: str | None) -> datetime | None:
    if not raw:
        return None
    raw = raw.strip()
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        dt = datetime.fromisoformat(raw)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def load_history(directory: Path) -> list[RateLimitEntry]:
    entries: list[RateLimitEntry] = []
    if not directory.exists():
        return entries
    for path in sorted(directory.glob("ratelimit_*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        captured = parse_timestamp(payload.get("captured_utc"))
        if not captured:
            continue
        resources = payload.get("data", {}).get("resources", {})
        entries.append(RateLimitEntry(captured=captured, resources=resources))
    entries.sort(key=lambda entry: entry.captured)
    return entries


def build_series(entries: Sequence[RateLimitEntry], key: str) -> list[tuple[str, int]]:
    points: list[tuple[str, int]] = []
    for entry in entries:
        point = entry.as_series_point(key)
        if point is not None:
            points.append(point)
    return points


def summarize(series: Sequence[tuple[str, int]]) -> dict[str, float]:
    if not series:
        return {"min": 0, "avg": 0, "max": 0}
    values = [value for _, value in series]
    return {
        "min": min(values),
        "avg": round(mean(values), 2),
        "max": max(values),
    }


def build_tile(entries: Sequence[RateLimitEntry]) -> dict[str, object]:
    core = build_series(entries, "core")
    search = build_series(entries, "search")
    graphql = build_series(entries, "graphql")
    summary = {
        "core": summarize(core),
        "search": summarize(search),
        "graphql": summarize(graphql),
    }
    return {
        "title": "Rate-Limit (7d)",
        "series": {
            "core": core,
            "search": search,
            "graphql": graphql,
        },
        "summary": summary,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a rate-limit tile JSON document from historical captures"
    )
    parser.add_argument(
        "--history",
        default="connectors/history",
        help="Directory containing ratelimit_*.json captures",
    )
    parser.add_argument(
        "--out",
        default=".codex/reports/tiles/ratelimit_tile.json",
        help="Destination JSON file for the tile",
    )
    args = parser.parse_args(argv)

    history_dir = Path(args.history)
    entries = load_history(history_dir)
    tile = build_tile(entries)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(tile, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {out_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
