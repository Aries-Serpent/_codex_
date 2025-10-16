#!/usr/bin/env python
from __future__ import annotations

import subprocess
import sys


def main() -> None:
    """Summarize import-linter contract results in advisory mode."""

    try:
        proc = subprocess.run(
            ["lint-imports"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print(
            "[import-contracts] lint-imports not found; skipping summary",
            file=sys.stderr,
        )
        sys.exit(0)

    output = proc.stdout + "\n" + proc.stderr
    broken = 0
    contracts = 0

    for line in output.splitlines():
        if "Contract" in line and ":" in line:
            contracts += 1
        if "BROKEN" in line or "broken" in line:
            broken += 1

    print(
        f"[import-contracts] contracts={contracts} "
        f"broken={broken} exit={proc.returncode}"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
