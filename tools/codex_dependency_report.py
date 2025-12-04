#!/usr/bin/env python
"""Dependency report tool for _codex_.

Collects installed Python distributions using ``importlib.metadata`` and
writes a JSON report sorted by package name.
"""
from __future__ import annotations

import argparse
import json
import sys
from importlib import metadata
from pathlib import Path
from typing import Any, Dict, List


def _collect_packages() -> List[Dict[str, str]]:
    packages: List[Dict[str, str]] = []
    for dist in metadata.distributions():  # pragma: no cover (ordering)
        packages.append({"name": dist.metadata["Name"], "version": dist.version})
    packages.sort(key=lambda item: item["name"].lower())
    return packages


def build_report() -> Dict[str, Any]:
    packages = _collect_packages()
    return {
        "python_version": sys.version,
        "package_count": len(packages),
        "packages": packages,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate dependency report for _codex_.")
    parser.add_argument(
        "--out",
        type=str,
        default="codex_dependency_report.json",
        help="Output JSON path (default: codex_dependency_report.json)",
    )
    args = parser.parse_args(argv)

    report = build_report()
    out_path = Path(args.out).expanduser().resolve()
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote dependency report to {out_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
