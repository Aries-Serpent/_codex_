#!/usr/bin/env python3
"""Copy preset pre-commit config based on lint policy."""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / ".codex" / "lint-policy.json"


def main() -> None:
    """Select pre-commit preset via env override or recorded policy."""
    requested = os.environ.get("LINT_POLICY")
    if requested not in (None, "", "ruff", "hybrid"):
        msg = f"Unknown LINT_POLICY={requested}"
        raise SystemExit(msg)
    if requested in ("ruff", "hybrid"):
        policy = requested
    else:
        js = json.loads(POLICY.read_text()) if POLICY.exists() else {"policy": "hybrid"}
        policy = js["policy"]
    src = ROOT / f".pre-commit-{policy}.yaml"
    dst = ROOT / ".pre-commit-config.yaml"
    shutil.copyfile(src, dst)
    sys.stdout.write(f"[pre-commit] selected policy: {policy}\n")


if __name__ == "__main__":
    main()
