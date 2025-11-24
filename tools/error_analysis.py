"""Lightweight analyzer for SessionLogger outputs.

Reads `.codex/logs/session_*.jsonl` files, groups errors by type/context,
prints a summary that can be consumed by automation.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

LOG_DIR = Path(".codex") / "logs"


def _iter_events(paths: Iterable[Path]):
    for path in paths:
        try:
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            continue


def summarize(log_dir: Path = LOG_DIR) -> dict:
    paths = sorted(log_dir.glob("session_*.jsonl"))
    errors = Counter()
    contexts = defaultdict(Counter)
    total = 0
    for event in _iter_events(paths):
        total += 1
        etype = event.get("event_type", "unknown")
        if etype == "error":
            err_type = event.get("data", {}).get("error_type") or event.get("error_type") or "unknown"
            errors[err_type] += 1
            ctx = event.get("data", {}).get("context") or event.get("context") or {}
            if isinstance(ctx, dict):
                for key, value in ctx.items():
                    contexts[key][str(value)] += 1
    return {"total_events": total, "error_types": errors, "contexts": {k: dict(v) for k, v in contexts.items()}}


def main() -> int:
    log_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else LOG_DIR
    summary = summarize(log_dir)
    if summary["total_events"] == 0:
        print("no events found", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
