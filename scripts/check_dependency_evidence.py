#!/usr/bin/env python
"""
check_dependency_evidence.py — Minimal schema validation for dependency_ops.jsonl

Validates that each non-empty JSON line contains required keys:
  - ts, action, tool

Exit codes:
  0 = OK
  2 = Malformed or missing required keys
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import json
import sys
from pathlib import Path

REQUIRED = {"ts", "action", "tool"}
EVIDENCE = Path(".codex/evidence/dependency_ops.jsonl")


def main() -> int:
    if not EVIDENCE.exists():
        print(f"[evidence] file missing: {EVIDENCE}", file=sys.stderr)
        return 0  # Not fatal in early pipelines

    bad = 0
    with EVIDENCE.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                print(f"[schema] line {i} invalid JSON", file=sys.stderr)
                bad += 1
                continue
            missing = REQUIRED - set(obj.keys())
            if missing:
                print(f"[schema] line {i} missing keys: {sorted(missing)}", file=sys.stderr)
                bad += 1

    if bad:
        print(f"[schema] FAIL — {bad} bad line(s)", file=sys.stderr)
        return 2
    print("[schema] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
