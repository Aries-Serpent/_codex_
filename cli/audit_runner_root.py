#!/usr/bin/env python
"""
Shim: delegates to scripts/space_traversal/audit_runner.py
Kept for backward compatibility with older invocations.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence


def _ensure_repo_root_on_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    repo_str = str(repo_root)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)


def main(argv: Sequence[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    try:
        from scripts.space_traversal.audit_runner import (
            main as _runner_main,  # type: ignore
        )
    except Exception as exc:  # pragma: no cover
        print("Failed to load scripts/space_traversal/audit_runner.py:", exc, file=sys.stderr)
        return 1
    _runner_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
