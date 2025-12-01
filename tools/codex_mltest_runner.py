#!/usr/bin/env python
"""Run pytest subsets based on ML Test Score categories.

This script:
- Reads `codex_ml_test_map.yaml`.
- Accepts one or more categories: data, model, infrastructure, regression, performance.
- Runs pytest restricted to the test paths for those categories.
- Emits a very small, machine-readable summary to stdout.

Design:
- Multiple categories are merged (unique test paths).
- If no category is provided, all categories are used.
- This is strictly local/offline, no CI or Actions integration.
"""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml


def _load_map(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("ML test map YAML must be a mapping at top level")
    cats = data.get("categories")
    if not isinstance(cats, dict):
        raise ValueError("ML test map missing 'categories' mapping")
    return cats


def _collect_tests(cats: Dict[str, Any], selected: List[str]) -> List[str]:
    tests: Set[str] = set()
    if not selected:
        selected = sorted(cats.keys())

    for name in selected:
        meta = cats.get(name)
        if not isinstance(meta, dict):
            continue
        tlist = meta.get("tests") or []
        if isinstance(tlist, list):
            for t in tlist:
                if isinstance(t, str):
                    tests.add(t)
    return sorted(tests)


def _run_pytest(tests: List[str]) -> int:
    if not tests:
        print("No tests to run for selected categories; exiting with 0.")
        return 0
    cmd = ["pytest", "-q"] + tests
    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, check=False)
    return proc.returncode


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run pytest by ML Test Score categories.")
    parser.add_argument(
        "--map",
        type=str,
        default="codex_ml_test_map.yaml",
        help="Path to ML test map YAML (default: codex_ml_test_map.yaml).",
    )
    parser.add_argument(
        "--category",
        "-c",
        action="append",
        dest="categories",
        default=None,
        help="Category to run (can be specified multiple times). "
        "If omitted, all categories are run.",
    )
    parser.add_argument(
        "--json-summary",
        type=str,
        default=None,
        help="Optional path to write a JSON summary of the run.",
    )
    args = parser.parse_args(argv)

    cats = _load_map(Path(args.map).expanduser().resolve())
    selected = args.categories or []
    tests = _collect_tests(cats, selected)
    rc = _run_pytest(tests)

    summary = {
        "categories": selected or sorted(cats.keys()),
        "tests": tests,
        "return_code": rc,
    }
    if args.json_summary:
        out = Path(args.json_summary).expanduser().resolve()
        out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"Wrote ML test summary to {out}")

    print("MLTEST_SUMMARY_JSON:", json.dumps(summary, sort_keys=True))
    return rc


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
