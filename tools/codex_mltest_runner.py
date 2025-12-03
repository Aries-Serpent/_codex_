#!/usr/bin/env python
"""Run pytest targets based on ML Test Score categories.

Reads:
- codex_ml_test_map.yaml

Executes pytest for tests whose `category` matches requested categories.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools import codex_mltest_map_validate as map_validate


def _load_map(path: Path) -> Dict[str, Any]:
    data = map_validate.load_ml_test_map(path)
    # Allow a simplified structure with top-level tests list by reshaping into
    # categories keyed by their declared category (defaulting to
    # "uncategorized").
    if isinstance(data, dict):
        categories = data.get("categories")
        tests_list = data.get("tests")
        if not isinstance(categories, dict) and isinstance(tests_list, list):
            cat_map: Dict[str, Dict[str, List[str]]] = {}
            for entry in tests_list:
                category = entry.get("category", "uncategorized")
                target = entry.get("pytest_target") or entry.get("target")
                if not target:
                    continue
                cat_map.setdefault(category, {}).setdefault("tests", []).append(target)
            data["categories"] = cat_map
    map_validate.validate_structure(data)
    return data


def _collect_tests(categories: Dict[str, Any], selected: Optional[List[str]]) -> List[str]:
    if selected:
        names = set(selected)
    else:
        names = set(categories.keys())

    collected: List[str] = []
    seen = set()
    for name in sorted(categories.keys()):
        if name not in names:
            continue
        tests = categories[name].get("tests", []) or []
        for t in tests:
            if t not in seen:
                collected.append(t)
                seen.add(t)
    return collected


def _collect_tests_with_categories(
    categories: Dict[str, Any], selected: Optional[List[str]]
) -> List[tuple[str, str]]:
    targets: List[tuple[str, str]] = []
    if selected:
        names = selected
    else:
        names = sorted(categories.keys())
    for name in names:
        tests = categories.get(name, {}).get("tests", []) or []
        for t in tests:
            targets.append((t, name))
    return targets


def run_tests(repo_root: Path, targets: List[tuple[str, str]]) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    overall_rc = 0
    for target, category in targets:
        cmd_list = ["pytest", target, "-q"]
        try:
            proc = subprocess.run(
                cmd_list,
                cwd=str(repo_root),
                check=False,
                capture_output=True,
                text=True,
            )
            rc = proc.returncode
            stdout = proc.stdout
            stderr = proc.stderr
        except TypeError:
            proc = subprocess.run(cmd_list, check=False)  # type: ignore[arg-type]
            rc = getattr(proc, "returncode", 1)
            stdout = getattr(proc, "stdout", "")
            stderr = getattr(proc, "stderr", "")
        if rc != 0:
            overall_rc = 1
        results.append(
            {
                "target": target,
                "category": category,
                "cmd": cmd_list,
                "returncode": rc,
                "stdout": stdout,
                "stderr": stderr,
            }
        )
    return {"overall_returncode": overall_rc, "results": results}


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run ML Test Score categories via pytest."
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=".",
        help="Repository root (default: current directory).",
    )
    parser.add_argument(
        "--category",
        "-c",
        action="append",
        default=None,
        help="Category to run (may be repeated). If omitted, all tests run.",
    )
    parser.add_argument(
        "--map",
        type=str,
        default="codex_ml_test_map.yaml",
        help="Test map YAML path (default: codex_ml_test_map.yaml).",
    )
    parser.add_argument(
        "--json-summary",
        type=str,
        default="codex_mltest_summary.json",
        help="JSON summary path (default: codex_mltest_summary.json).",
    )
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    mapping = _load_map(root / args.map)
    categories = mapping.get("categories", {})
    targets = _collect_tests_with_categories(categories, args.category)
    result = run_tests(root, targets)

    out_raw = Path(args.json_summary)
    out = out_raw if out_raw.is_absolute() else root / out_raw
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote MLTest summary to {out}")
    return int(result["overall_returncode"])


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
