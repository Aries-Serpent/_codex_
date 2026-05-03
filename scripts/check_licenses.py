"""
Check Licenses

Purpose:
    Main execution script

Usage:
    python scripts/check_licenses.py [options]

    Examples:
    $ python scripts/check_licenses.py --help

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

import logging

logger = logging.getLogger(__name__)
#!/usr/bin/env python

import json
import subprocess
import sys
from collections.abc import Iterable

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
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
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
