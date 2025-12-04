#!/usr/bin/env python3
"""Aggregate multiple SARIF files into a single report.

This utility performs a lightweight concatenation of SARIF runs, preserving
the original `version` field from the first input file. Missing files are
treated as empty and do not cause the aggregation to fail.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Sequence


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate SARIF files")
    parser.add_argument("--in", dest="inputs", nargs="+", required=True, help="Input SARIF files")
    parser.add_argument("--out", required=True, help="Output aggregated SARIF file")
    return parser.parse_args(list(argv) if argv is not None else None)


def load_sarif(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def aggregate_sarif(paths: List[Path]) -> dict:
    aggregated: dict = {"version": "2.1.0", "runs": []}
    version_set = False
    for p in paths:
        sarif = load_sarif(p)
        if not sarif:
            continue
        if not version_set and "version" in sarif:
            aggregated["version"] = sarif.get("version", aggregated["version"])
            version_set = True
        runs = sarif.get("runs", []) or []
        if isinstance(runs, list):
            aggregated["runs"].extend(runs)
    return aggregated


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    inputs = [Path(p) for p in args.inputs]
    out_path = Path(args.out)
    sarif = aggregate_sarif(inputs)
    out_path.write_text(json.dumps(sarif, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Aggregated SARIF written to {out_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
