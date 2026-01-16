#!/usr/bin/env python
"""
Verify Dependency Hygiene

Purpose:
    Main execution script

Usage:
    python scripts/verify_dependency_hygiene.py [options]
    
    Examples:
    $ python scripts/verify_dependency_hygiene.py --help

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
verify_dependency_hygiene.py — Summarize dependency evidence and assert vendor hygiene

- Prints counts per 'action' in dependency_ops.jsonl
- Warns if any DEPENDENCY_VENDOR_PURGE events leave non-empty vendor_list_after
- Exits non-zero (7) if vendor residue persists while CODEX_FAIL_ON_GPU_RESIDUE=1

This is a convenience complement to nox session 'verify_hygiene'.
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import json
import os
import sys
from pathlib import Path
from typing import Any

EVIDENCE = Path(".codex/evidence/dependency_ops.jsonl")


def load_lines() -> list[dict[str, Any]]:
    if not EVIDENCE.exists():
        print("[verify_hygiene] evidence file missing (skipping).")
        return []
    data: list[dict[str, Any]] = []
    for i, line in enumerate(EVIDENCE.read_text(encoding="utf-8").splitlines(), start=1):
        s = line.strip()
        if not s:
            continue
        try:
            data.append(json.loads(s))
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            print(f"[verify_hygiene] malformed evidence at line {i}", file=sys.stderr)
    return data


def main() -> int:
    rows = load_lines()
    counts: dict[str, int] = {}
    for r in rows:
        counts[r.get("action", "UNKNOWN")] = counts.get(r.get("action", "UNKNOWN"), 0) + 1
    print("[verify_hygiene] action counts:")
    for k in sorted(counts.keys()):
        print(f"  - {k}: {counts[k]}")

    # Residue check on purge events
    residue: list[str] = []
    for r in rows:
        if r.get("action") == "DEPENDENCY_VENDOR_PURGE":
            after = (r.get("vendor_list_after") or "").strip()
            if after:
                residue.append(after)
    if residue:
        print(f"[verify_hygiene] WARNING — Residual vendor lists after purge detected: {residue}")
        if os.getenv("CODEX_FAIL_ON_GPU_RESIDUE", "0") == "1":
            return 7
    else:
        print("[verify_hygiene] OK — No vendor residue after purge.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
