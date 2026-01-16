#!/usr/bin/env python
"""
Trend Aggregate

Purpose:
    Main execution script

Usage:
    python scripts/archive/trend_aggregate.py [options]
    
    Examples:
    $ python scripts/archive/trend_aggregate.py --help

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


"""
import logging
logger = logging.getLogger(__name__)
Trend Aggregator (P5)

Aggregates historical capability_scored.json files into trend_scores.json:
- Scan audit_artifacts/ for dated snapshots (or user-provided glob DIRS)
- Build per-capability chronological score list
- Compute simple deltas & percent change from first to last
- Optionally produce mini sparkline ASCII for console preview

Knobs:
  TREND_LIMIT=30 -> max snapshots considered
  TREND_SPARKLINE=1 -> include sparkline text
"""
from __future__ import annotations

import glob
import json
import os
import sys
from pathlib import Path

OUT = Path("audit_artifacts/trend_scores.json")


def sparkline(series: list[float]) -> str:
    if not series:
        return ""
    chars = "▁▂▃▄▅▆▇█"
    mn, mx = min(series), max(series)
    rng = mx - mn if mx != mn else 1e-9
    return "".join(chars[int((v - mn) / rng * (len(chars) - 1))] for v in series)


def find_score_files(limit: int) -> list[Path]:
    pattern = "audit_artifacts/capabilities_scored*.json"
    files = [Path(p) for p in glob.glob(pattern)]
    files.sort(key=lambda p: p.stat().st_mtime)
    return files[-limit:]


def load_scores(p: Path) -> dict[str, float]:
    try:
        data = json.loads(p.read_text())
    except Exception:
        return {}
    result = {}
    for c in data.get("capabilities", []):
        result[c["id"]] = c.get("score", 0.0)
    return result


def main():
    limit = int(os.getenv("TREND_LIMIT", "30"))
    spark_enable = os.getenv("TREND_SPARKLINE", "0") in {"1", "true", "TRUE"}

    files = find_score_files(limit)
    if not files:
        print("[INFO] No historical scored files found.")
        return 0

    history: dict[str, list[float]] = {}
    timestamps = []

    for f in files:
        scores = load_scores(f)
        timestamps.append(f.name)
        for cid, sc in scores.items():
            history.setdefault(cid, []).append(sc)

    payload = {"capabilities": [], "snapshots": timestamps}

    for cid, series in history.items():
        delta = series[-1] - series[0]
        pct = (delta / series[0]) if series[0] else 0.0
        entry = {
            "id": cid,
            "scores": [round(s, 4) for s in series],
            "delta": round(delta, 4),
            "pct_change": round(pct, 4),
        }
        if spark_enable:
            entry["sparkline"] = sparkline(series)
        payload["capabilities"].append(entry)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[INFO] Trend scores written: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
