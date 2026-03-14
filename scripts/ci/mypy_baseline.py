#!/usr/bin/env python3
"""
mypy_baseline.py — Anti-regression mypy gate for CI.

Purpose
-------
Runs mypy against ``src/`` and compares the current error count against a
stored baseline.  CI **passes** when the count is equal to or below the
baseline (no new errors introduced).  CI **fails** when the count exceeds
the baseline (new type errors were added).

The baseline is stored in ``.mypy_baseline`` at the repository root as a
single integer.  It is updated manually by running::

    python scripts/ci/mypy_baseline.py --update

Design
------
- Non-strict: ignores missing imports / stubs (matches existing mypy.ini).
- Ratchet: baseline can only go down, never up (enforced by CI).
- Exit 0  — count ≤ baseline (pass, no regression).
- Exit 1  — count > baseline (fail, new type errors introduced).
- Exit 2  — baseline file missing and ``--require-baseline`` passed.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_FILE = REPO_ROOT / ".mypy_baseline"
SRC_DIR = REPO_ROOT / "src"

# Mypy flags that match the project's existing mypy.ini / pyproject.toml config
MYPY_FLAGS = [
    "--ignore-missing-imports",
    "--no-error-summary",
    "--no-pretty",
]


def run_mypy() -> int:
    """Run mypy and return the number of error lines."""
    result = subprocess.run(
        [sys.executable, "-m", "mypy", str(SRC_DIR)] + MYPY_FLAGS,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    error_lines = [
        line for line in result.stdout.splitlines() if ": error:" in line
    ]
    return len(error_lines)


def read_baseline() -> int | None:
    """Return the stored baseline count, or None if the file does not exist."""
    if not BASELINE_FILE.exists():
        return None
    try:
        return int(BASELINE_FILE.read_text().strip())
    except ValueError:
        return None


def write_baseline(count: int) -> None:
    """Persist a new baseline count."""
    BASELINE_FILE.write_text(f"{count}\n")
    print(f"✅ Baseline updated → {count} errors")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--update",
        action="store_true",
        help="Re-run mypy and overwrite .mypy_baseline with the new count.",
    )
    parser.add_argument(
        "--require-baseline",
        action="store_true",
        help="Exit 2 if .mypy_baseline does not exist (for CI enforcement).",
    )
    args = parser.parse_args()

    print(f"🔍 Running mypy on {SRC_DIR.relative_to(REPO_ROOT)} …")
    current = run_mypy()
    print(f"   mypy errors found: {current}")

    if args.update:
        write_baseline(current)
        return 0

    baseline = read_baseline()

    if baseline is None:
        if args.require_baseline:
            print(
                "::error::'.mypy_baseline' not found. "
                "Run `python scripts/ci/mypy_baseline.py --update` to create it.",
                file=sys.stderr,
            )
            return 2
        # First run — create the baseline automatically and pass.
        write_baseline(current)
        print("ℹ️  No baseline found — created one from current run. CI passes.")
        return 0

    delta = current - baseline
    if delta > 0:
        print(
            f"::error::mypy regression: {current} errors > baseline {baseline} "
            f"(+{delta} new error(s)). Fix the type errors or run "
            "`python scripts/ci/mypy_baseline.py --update` to reset the baseline.",
            file=sys.stderr,
        )
        print(f"❌ FAIL — {current} errors (+{delta} above baseline {baseline})")
        return 1

    arrow = f"↓ {-delta}" if delta < 0 else "="
    print(f"✅ PASS — {current} errors ({arrow} vs baseline {baseline})")
    if delta < 0:
        print(
            f"ℹ️  Error count improved by {-delta}. "
            "Consider running `python scripts/ci/mypy_baseline.py --update` "
            "to lower the baseline and lock in the improvement."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
