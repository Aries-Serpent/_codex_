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
import platform
import sys
from pathlib import Path
from typing import Any, Dict, List


def _installed_packages() -> List[Dict[str, str]]:
    try:
        import pkg_resources  # type: ignore
    except Exception:
        return []
    pkgs = []
    for dist in pkg_resources.working_set:  # pragma: no cover (ordering)
        pkgs.append({"name": dist.project_name, "version": dist.version})
    pkgs.sort(key=lambda d: d["name"].lower())
    return pkgs


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
