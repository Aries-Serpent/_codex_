#!/usr/bin/env python
"""Environment snapshot tool for `_codex_`.

Captures a small JSON summary of:
- Python version and executable
- Platform information
- Installed packages (best-effort)
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from importlib import metadata
from pathlib import Path
from typing import Any, Dict, List


def _installed_packages() -> List[Dict[str, str]]:
    packages: List[Dict[str, str]] = []
    for dist in metadata.distributions():  # pragma: no cover (ordering)
        packages.append({"name": dist.metadata["Name"], "version": dist.version})
    packages.sort(key=lambda d: d["name"].lower())
    return packages


def _environment_variables() -> Dict[str, str]:
    captured: Dict[str, str] = {}
    for key, value in sorted(os.environ.items()):
        captured[key] = value
    return captured


def build_snapshot() -> Dict[str, Any]:
    return {
        "python": {
            "version": sys.version,
            "executable": sys.executable,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "environment": _environment_variables(),
        "installed_packages": _installed_packages(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Capture _codex_ environment snapshot.")
    parser.add_argument(
        "--out",
        type=str,
        default="codex_env_snapshot.json",
        help="Output JSON path (default: codex_env_snapshot.json).",
    )
    args = parser.parse_args(argv)

    snap = build_snapshot()
    out = Path(args.out).expanduser().resolve()
    out.write_text(json.dumps(snap, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote environment snapshot to {out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
