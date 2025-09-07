#!/usr/bin/env python
"""Simple license checker using pip-licenses."""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Iterable

ALLOWED: set[str] = {"MIT", "Apache-2.0", "BSD-3-Clause", "BSD", "ISC"}


def _run_pip_licenses() -> Iterable[dict]:
    proc = subprocess.run(
        ["pip-licenses", "--format=json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout or "[]")


def main() -> int:
    try:
        pkgs = _run_pip_licenses()
    except FileNotFoundError:
        print("pip-licenses not installed; skipping", file=sys.stderr)
        return 0
    except subprocess.CalledProcessError as exc:
        print(f"pip-licenses failed: {exc}", file=sys.stderr)
        return 1
    bad = [p for p in pkgs if p.get("License") not in ALLOWED]
    if bad:
        names = ", ".join(f"{p['Name']} ({p['License']})" for p in bad)
        print(f"Disallowed licenses: {names}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
