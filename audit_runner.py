#!/usr/bin/env python
"""
Thin shim delegating to scripts/space_traversal/audit_runner.py
Rationale: single source of truth for the runner implementation.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    target = Path(__file__).parent / "scripts" / "space_traversal" / "audit_runner.py"
    if not target.exists():
        print(f"[shim] Target runner not found: {target}", file=sys.stderr)
        sys.exit(2)
    # Execute target as __main__ so CLI behaves identically
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
