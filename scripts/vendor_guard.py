#!/usr/bin/env python
"""
vendor_guard.py — Fail-fast scan for GPU vendor packages in CPU posture

Behavior:
  - Scans installed/available modules for nvidia-* / triton / torchtriton.
  - Respects CODEX_ALLOW_TRITON_CPU=1 to filter 'triton'.
  - If CODEX_FORCE_CPU=1 and any vendor present (after filter), exit code 1.
  - Emits a single JSON line to stdout with summary; errors to stderr.

Example:
  python scripts/vendor_guard.py
"""

from __future__ import annotations

import json
import os
import pkgutil
import sys
import time
from typing import List


def utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def scan() -> List[str]:
    mods = []
    for m in pkgutil.iter_modules():
        n = m.name
        if n.startswith("nvidia-") or n in {"triton", "torchtriton"}:
            mods.append(n)
    if os.getenv("CODEX_ALLOW_TRITON_CPU", "1") == "1":
        mods = [v for v in mods if v != "triton"]
    return sorted(set(mods))


def main() -> int:
    vendors = scan()
    record = {
        "ts": utc(),
        "action": "DEPENDENCY_VENDOR_SCAN",
        "vendors": vendors,
        "cpu_only": os.getenv("CODEX_FORCE_CPU", "1") == "1",
        "note": "posture guard",
    }
    out = json.dumps(record, ensure_ascii=False)
    # Print to stdout if clean; stderr if problem
    if record["cpu_only"] and vendors:
        print(out, file=sys.stderr)
        return 1
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
