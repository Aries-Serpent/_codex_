#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / ".codex" / "lint-policy.json"


def main():
    requested = os.environ.get("LINT_POLICY")
    if requested not in (None, "", "ruff", "hybrid"):
        raise SystemExit(f"Unknown LINT_POLICY={requested}")
    if requested in ("ruff", "hybrid"):
        policy = requested
    else:
        js = json.loads(POLICY.read_text()) if POLICY.exists() else {"policy": "hybrid"}
        policy = js["policy"]
    src = ROOT / (f".pre-commit-{policy}.yaml")
    dst = ROOT / ".pre-commit-config.yaml"
    shutil.copyfile(src, dst)
    print(f"[pre-commit] selected policy: {policy}")


if __name__ == "__main__":
    main()
