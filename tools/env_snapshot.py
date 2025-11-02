#!/usr/bin/env python3
"""
Capture environment snapshot for status reports.

Output:
  env_snapshot.json with python, os, pip_freeze, etc.

Usage:
  python tools/env_snapshot.py
"""
from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def main(argv=None) -> int:
    snapshot = {
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "os": platform.platform(),
        "hostname": platform.node(),
        "pip_freeze": [],
    }

    try:
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            snapshot["pip_freeze"] = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        pass

    out = Path("env_snapshot.json")
    out.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
