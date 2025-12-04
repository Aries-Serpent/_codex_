#!/usr/bin/env python
"""Category-driven ML test runner for _codex_."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Mapping

import yaml


@dataclass
class CategoryResult:
    category: str
    tests: List[str]
    returncode: int


def _load_map(path: Path) -> Mapping[str, Any]:
    return yaml.safe_load(path.read_text()) or {}


def _normalize_categories(data: Mapping[str, Any]) -> Mapping[str, Any]:
    if "categories" in data:
        return data.get("categories", {})
    normalized: dict[str, Any] = {}
    for entry in data.get("tests", []) or []:
        category = entry.get("category", "default")
        target = entry.get("pytest_target")
        if category not in normalized:
            normalized[category] = {"tests": []}
        if target:
            normalized[category]["tests"].append(target)
    return normalized


def _collect_tests(categories: Mapping[str, Any], selected: Iterable[str]) -> List[str]:
    ordered: List[str] = []
    for category in selected:
        info = categories.get(category) or {}
        for test_target in info.get("tests", []):
            if test_target not in ordered:
                ordered.append(test_target)
    return ordered


def _run_pytest(targets: List[str], repo_root: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    if not targets:
        return subprocess.CompletedProcess(args=["pytest"], returncode=0)
    command = ["pytest", *targets]
    try:
        return subprocess.run(command, cwd=str(repo_root), check=False, env=env)
    except TypeError:
        return subprocess.run(command, check=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run mapped ML test categories with pytest.")
    parser.add_argument("--map", type=Path, default=Path("codex_ml_test_map.yaml"))
    parser.add_argument("--category", action="append", dest="categories")
    parser.add_argument("--json-summary", type=Path, default=Path("codex_mltest_summary.json"))
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args(argv)

    data = _load_map(args.map)
    categories = _normalize_categories(data)
    selected = args.categories if args.categories else list(categories.keys())
    targets = _collect_tests(categories, selected)

    result = _run_pytest(targets, args.repo_root)

    summary_results = [CategoryResult(category=cat, tests=categories.get(cat, {}).get("tests", []), returncode=result.returncode) for cat in selected]
    summary = {
        "overall_returncode": result.returncode,
        "results": [
            {
                "category": r.category,
                "tests": r.tests,
                "returncode": r.returncode,
            }
            for r in summary_results
        ],
    }

    out_path = args.json_summary
    if not out_path.is_absolute():
        out_path = (args.repo_root / out_path).resolve()
    else:
        out_path = out_path.expanduser().resolve()
    out_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote ML test summary to {out_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
