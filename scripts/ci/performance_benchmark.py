#!/usr/bin/env python3
"""Performance benchmarking framework for CI pipeline health.

Runs timed benchmarks against key operations and reports results.

Usage:
    python scripts/ci/performance_benchmark.py          # Human-readable
    python scripts/ci/performance_benchmark.py --json   # JSON output
    python scripts/ci/performance_benchmark.py --ci     # CI summary
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class BenchmarkResult:
    """Result of a single benchmark."""

    name: str
    duration_seconds: float
    success: bool
    details: str = ""


def _run_timed(cmd: list[str], timeout: int = 120) -> BenchmarkResult:
    """Run a command and time it."""
    name = " ".join(cmd[:min(3, len(cmd))])
    start = time.monotonic()
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, cwd=ROOT, timeout=timeout,
        )
        elapsed = time.monotonic() - start
        return BenchmarkResult(name, elapsed, r.returncode == 0,
                               f"exit={r.returncode}")
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        return BenchmarkResult(name, elapsed, False, "timeout")
    except FileNotFoundError:
        elapsed = time.monotonic() - start
        return BenchmarkResult(name, elapsed, False, "not found")


def run_benchmarks() -> list[BenchmarkResult]:
    """Run all benchmarks."""
    results = []

    # 1. Ruff lint speed
    results.append(_run_timed(
        ["python", "-m", "ruff", "check", "src/", "-q", "--statistics"],
    ))

    # 2. Python syntax check (sample)
    results.append(_run_timed(
        ["python", "-m", "py_compile", "src/codex/__init__.py"],
    ))

    # 3. Test collection (dry run)
    results.append(_run_timed(
        ["python", "-m", "pytest", "--collect-only", "-q",
         "tests/ci/", "--no-header"],
        timeout=60,
    ))

    # 4. Import speed test
    start = time.monotonic()
    try:
        subprocess.run(
            ["python", "-c", "import codex"],
            capture_output=True, text=True, cwd=ROOT, timeout=30,
        )
        success = True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        success = False
    elapsed = time.monotonic() - start
    results.append(BenchmarkResult("import codex", elapsed, success))

    # 5. File count benchmark
    start = time.monotonic()
    py_count = len(list(ROOT.glob("**/*.py")))
    elapsed = time.monotonic() - start
    results.append(BenchmarkResult(
        "glob **/*.py", elapsed, True, f"{py_count} files",
    ))

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Performance Benchmarking")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", help="Write to file")
    parser.add_argument("--ci", action="store_true")
    args = parser.parse_args()

    results = run_benchmarks()

    if args.json:
        data = {"benchmarks": [asdict(r) for r in results]}
        output = json.dumps(data, indent=2)
    else:
        lines = ["Performance Benchmarks", "=" * 40, ""]
        for r in results:
            status = "✅" if r.success else "❌"
            lines.append(f"  {status} {r.name:30s} {r.duration_seconds:6.2f}s  {r.details}")
        total = sum(r.duration_seconds for r in results)
        lines.append(f"\n  Total: {total:.2f}s")
        output = "\n".join(lines)

    print(output)

    if args.output:
        Path(args.output).write_text(output)

    if args.ci:
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a") as f:
                f.write("\n## Performance Benchmarks\n\n")
                for r in results:
                    status = "✅" if r.success else "❌"
                    f.write(f"- {status} **{r.name}**: {r.duration_seconds:.2f}s\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
