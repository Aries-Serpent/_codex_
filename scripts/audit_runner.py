#!/usr/bin/env python
"""
Shim: delegates to scripts/space_traversal/audit_runner.py
Kept for backward compatibility with older invocations.
"""
from __future__ import annotations

import sys


def main() -> None:
    try:
        from scripts.space_traversal.audit_runner import main as _runner_main  # type: ignore
    except Exception as exc:  # pragma: no cover
        print("Failed to load scripts/space_traversal/audit_runner.py:", exc, file=sys.stderr)
        raise SystemExit(1)
    _runner_main()


if __name__ == "__main__":
    main()
