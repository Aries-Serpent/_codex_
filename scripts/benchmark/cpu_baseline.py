#!/usr/bin/env python3
"""CPU Performance Baseline — Primary Test Machine (P10-04).

Establishes a reproducible, hardware-agnostic CPU-mode performance baseline
for the Intel Core Ultra 5 135U vPro primary test machine.

No CUDA, no GPU, no external services required.  All benchmarks run in-process
and complete in < 60 s on the primary machine.

Usage::

    # Run full baseline (all suites)
    python scripts/benchmark/cpu_baseline.py

    # Run specific suite
    python scripts/benchmark/cpu_baseline.py --suite import

    # Write JSON report
    python scripts/benchmark/cpu_baseline.py --json /tmp/cpu_baseline.json

    # Compare against a stored baseline
    python scripts/benchmark/cpu_baseline.py --compare /tmp/cpu_baseline.json

Exit codes:
    0 — all benchmarks within tolerance (or baseline stored)
    1 — one or more benchmarks exceed regression threshold (>= 2× baseline)
    2 — argument / environment error
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# Benchmark registry
# ─────────────────────────────────────────────────────────────────────────────

_BENCHMARKS: dict[str, dict[str, Any]] = {}


def _bench(suite: str, name: str, reps: int = 1):
    """Decorator that registers a benchmark function."""

    def _decorator(fn):
        _BENCHMARKS.setdefault(suite, {})[name] = {"fn": fn, "reps": reps}
        return fn

    return _decorator


# ─────────────────────────────────────────────────────────────────────────────
# Suite: import — critical module import latency
# ─────────────────────────────────────────────────────────────────────────────


@_bench("import", "import_pathlib", reps=1000)
def _bench_import_pathlib():
    import pathlib  # noqa: F401, PLC0415
    return pathlib.Path


@_bench("import", "import_json", reps=1000)
def _bench_import_json():
    import json as _j  # noqa: F401, PLC0415
    return _j.dumps


@_bench("import", "import_logging", reps=500)
def _bench_import_logging():
    import logging  # noqa: F401, PLC0415
    return logging.getLogger


# ─────────────────────────────────────────────────────────────────────────────
# Suite: cpu — raw CPU throughput (platform-independent)
# ─────────────────────────────────────────────────────────────────────────────


@_bench("cpu", "sha256_1MB", reps=100)
def _bench_sha256_1mb():
    data = b"x" * (1024 * 1024)
    return hashlib.sha256(data).hexdigest()


@_bench("cpu", "int_sort_10k", reps=200)
def _bench_int_sort():
    import random  # noqa: PLC0415
    data = [random.randint(0, 10_000) for _ in range(10_000)]
    return sorted(data)[-1]


@_bench("cpu", "math_sqrt_loop", reps=500)
def _bench_math_sqrt():
    total = 0.0
    for i in range(1, 10_001):
        total += math.sqrt(i)
    return total


@_bench("cpu", "json_roundtrip_100k_chars", reps=200)
def _bench_json_roundtrip():
    payload = {"key_" + str(i): "value_" + str(i) for i in range(500)}
    return json.loads(json.dumps(payload))


# ─────────────────────────────────────────────────────────────────────────────
# Suite: io — file I/O throughput (tmpfs / SSD)
# ─────────────────────────────────────────────────────────────────────────────


@_bench("io", "write_read_1MB_tmpfile", reps=50)
def _bench_write_read_1mb():
    import tempfile  # noqa: PLC0415
    data = b"z" * (1024 * 1024)
    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.write(data)
        f.flush()
        f.seek(0)
        return len(f.read())


@_bench("io", "path_glob_tests_dir", reps=10)
def _bench_path_glob():
    tests_dir = Path(__file__).parents[2] / "tests"
    if not tests_dir.exists():
        return 0
    return sum(1 for _ in tests_dir.rglob("*.py"))


# ─────────────────────────────────────────────────────────────────────────────
# Suite: ml — lightweight CPU-mode ML ops (no CUDA required)
# ─────────────────────────────────────────────────────────────────────────────


@_bench("ml", "torch_matmul_64x64_cpu", reps=200)
def _bench_torch_matmul():
    try:
        import torch  # noqa: PLC0415
        a = torch.randn(64, 64)
        b = torch.randn(64, 64)
        return float(torch.mm(a, b).sum())
    except ImportError:
        return None  # torch not installed — skip


@_bench("ml", "numpy_dot_1000x1000_cpu", reps=50)
def _bench_numpy_dot():
    try:
        import numpy as np  # noqa: PLC0415
        a = np.random.randn(1000, 1000).astype(np.float32)
        return float(np.dot(a, a.T).sum())
    except ImportError:
        return None  # numpy not installed — skip


# ─────────────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────────────


def _run_suite(suite_name: str, suite: dict[str, Any]) -> dict[str, Any]:
    results = {}
    for bench_name, spec in suite.items():
        fn = spec["fn"]
        reps = spec["reps"]
        try:
            # Warm-up (1 rep)
            fn()
            # Timed run
            t0 = time.perf_counter()
            for _ in range(reps):
                fn()
            elapsed = time.perf_counter() - t0
            per_rep_us = (elapsed / reps) * 1_000_000
            results[bench_name] = {
                "reps": reps,
                "total_s": round(elapsed, 4),
                "per_rep_us": round(per_rep_us, 2),
                "status": "ok",
            }
        except Exception as exc:  # noqa: BLE001
            results[bench_name] = {
                "reps": reps,
                "total_s": None,
                "per_rep_us": None,
                "status": f"error: {exc}",
            }
    return results


def run_benchmarks(suites: list[str] | None = None) -> dict[str, Any]:
    """Run all (or selected) benchmark suites and return results dict."""
    import platform  # noqa: PLC0415

    results: dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "machine": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python": platform.python_version(),
            "cpu_count": os.cpu_count(),
        },
        "suites": {},
    }

    target_suites = suites or list(_BENCHMARKS.keys())
    for suite_name in target_suites:
        if suite_name not in _BENCHMARKS:
            print(f"  ⚠ unknown suite: {suite_name!r}", file=sys.stderr)
            continue
        t0 = time.perf_counter()
        suite_results = _run_suite(suite_name, _BENCHMARKS[suite_name])
        elapsed = time.perf_counter() - t0
        results["suites"][suite_name] = {
            "elapsed_s": round(elapsed, 3),
            "benchmarks": suite_results,
        }

    return results


def compare_with_baseline(current: dict, baseline: dict, threshold: float = 2.0) -> list[str]:
    """Return list of regressions (current > threshold × baseline per-rep time)."""
    regressions = []
    for suite, suite_data in current.get("suites", {}).items():
        baseline_suite = baseline.get("suites", {}).get(suite, {})
        for bench, bdata in suite_data.get("benchmarks", {}).items():
            if bdata.get("status") != "ok":
                continue
            base_bench = baseline_suite.get("benchmarks", {}).get(bench, {})
            if base_bench.get("status") != "ok":
                continue
            cur_us = bdata["per_rep_us"]
            base_us = base_bench["per_rep_us"]
            if base_us and base_us > 0 and cur_us > threshold * base_us:
                ratio = cur_us / base_us
                regressions.append(
                    f"{suite}/{bench}: {cur_us:.1f}µs vs baseline {base_us:.1f}µs ({ratio:.1f}× — REGRESSION)"
                )
    return regressions


def _print_results(results: dict) -> None:
    print(f"\n{'═' * 60}")
    print(f"  CPU Baseline — {results['machine']['platform']}")
    print(f"  Python {results['machine']['python']} | {results['machine']['cpu_count']} CPUs")
    print(f"{'═' * 60}")
    for suite_name, suite_data in results["suites"].items():
        print(f"\n  [{suite_name}] — {suite_data['elapsed_s']:.3f}s total")
        for bench, bdata in suite_data["benchmarks"].items():
            if bdata["status"] == "ok":
                print(f"    {bench:<40} {bdata['per_rep_us']:>10.2f} µs/rep")
            else:
                print(f"    {bench:<40} {'SKIP/ERROR':>10}")
    print(f"\n{'═' * 60}\n")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CPU performance baseline")
    parser.add_argument("--suite", choices=list(_BENCHMARKS.keys()), help="Run single suite")
    parser.add_argument("--json", metavar="PATH", help="Write JSON report to PATH")
    parser.add_argument("--compare", metavar="BASELINE_JSON", help="Compare against stored baseline")
    parser.add_argument("--threshold", type=float, default=2.0, help="Regression threshold multiplier (default 2.0×)")
    args = parser.parse_args(argv)

    suites = [args.suite] if args.suite else None
    print(f"Running CPU benchmarks (suites: {suites or 'all'})…")
    results = run_benchmarks(suites)
    _print_results(results)

    # Save JSON
    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(results, indent=2))
        print(f"JSON report written to: {out}")

    # Compare
    if args.compare:
        baseline_path = Path(args.compare)
        if not baseline_path.exists():
            print(f"Baseline not found ({baseline_path}); saving current run as baseline.")
            baseline_path.parent.mkdir(parents=True, exist_ok=True)
            baseline_path.write_text(json.dumps(results, indent=2))
            return 0
        baseline = json.loads(baseline_path.read_text())
        regressions = compare_with_baseline(results, baseline, args.threshold)
        if regressions:
            print(f"🔴 {len(regressions)} regression(s) detected:")
            for r in regressions:
                print(f"   {r}")
            return 1
        print(f"✅ No regressions (threshold: {args.threshold}×)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
