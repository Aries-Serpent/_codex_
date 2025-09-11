"""Fail if active GitHub workflows are present without opt-in."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> int:
    if os.environ.get("CODEX_ALLOW_CI") == "1":
        return 0
    wf_dir = Path(".github/workflows")
    if wf_dir.exists() and any(wf_dir.glob("*.yml")):
        print("Active workflows detected; set CODEX_ALLOW_CI=1 to proceed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
