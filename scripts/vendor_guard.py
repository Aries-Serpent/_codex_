#!/usr/bin/env python
"""
Vendor Guard

Purpose:
    Main execution script

Usage:
    python scripts/vendor_guard.py [options]

    Examples:
    $ python scripts/vendor_guard.py --help

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

import json
import os
import pkgutil
import sys
import time


def utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def scan() -> list[str]:
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
