"""
Test Pyramid Report — D7 exit criteria #3 helper.

Counts test functions per tier (unit / integration / e2e) and reports
the pyramid health ratio.

Usage:
    python scripts/ci/test_pyramid_report.py [--output PATH]
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def count_test_functions(directory: Path) -> int:
    """Count test functions (def test_*) in a directory tree."""
    count = 0
    for path in directory.rglob("test_*.py"):
        try:
            tree = ast.parse(path.read_text())
            count += sum(
                1 for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
            )
        except (SyntaxError, UnicodeDecodeError) as exc:
            print(f"WARNING: skipping {path}: {exc}", file=sys.stderr)
    return count


def classify_tests(tests_root: Path) -> dict[str, int]:
    """Classify tests into pyramid tiers."""
    integration_dirs = [tests_root / "integration"]
    e2e_dirs = [tests_root / "e2e", tests_root / "functional"]

    # Unit = all non-integration, non-e2e test dirs
    integration_count = sum(
        count_test_functions(d) for d in integration_dirs if d.exists()
    )
    e2e_count = sum(count_test_functions(d) for d in e2e_dirs if d.exists())

    # Total minus integration/e2e = unit proxy
    total = count_test_functions(tests_root)
    unit_count = total - integration_count - e2e_count

    return {
        "unit_tests": max(unit_count, 0),
        "integration_tests": integration_count,
        "e2e_tests": e2e_count,
        "total_tests": total,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tests-root", default="tests")
    parser.add_argument("--output", default=".codex/reports/test_pyramid_latest.json")
    args = parser.parse_args()

    root = Path(args.tests_root)
    if not root.exists():
        print(f"::error::Tests directory {root} not found", file=sys.stderr)
        sys.exit(1)

    counts = classify_tests(root)
    ratio = counts["unit_tests"] / max(counts["integration_tests"] + counts["e2e_tests"], 1)

    report = {
        "generated_at": _ts(),
        "tests_root": str(root),
        **counts,
        "pyramid_ratio": round(ratio, 2),
        "healthy_ratio_threshold": 4.0,
        "health": "✅ healthy" if ratio >= 4.0 else "⚠️ inverted",
    }

    print(json.dumps(report, indent=2))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2))

    print(f"Unit: {counts['unit_tests']}  "
          f"Integration: {counts['integration_tests']}  "
          f"E2E: {counts['e2e_tests']}  "
          f"Ratio: {ratio:.1f}x")

    if ratio >= 4.0:
        print("::notice::✅ D7 exit criteria #3 met: test pyramid ratio >= 4x")
    else:
        print(f"::warning::D7 pyramid ratio {ratio:.1f}x — target ≥ 4x unit-to-integration")


if __name__ == "__main__":
    main()
