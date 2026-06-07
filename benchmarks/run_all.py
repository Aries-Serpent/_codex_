"""
run_all.py — Master benchmark runner for gap 24.

Executes all three benchmark modules and writes a consolidated JSON report to
``benchmarks/results/benchmark_report.json``.

Usage::

    cd /path/to/_codex_
    python benchmarks/run_all.py

Options::

    --output PATH   Override the output file path.
    --repeats N     Number of repeats for training benchmark (default 3).
    --quiet         Suppress per-benchmark console output.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Resolve project root so sibling modules import correctly regardless of CWD
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent  # benchmarks/
_ROOT = _HERE.parent                     # repo root
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# ---------------------------------------------------------------------------
# Default output path
# ---------------------------------------------------------------------------

DEFAULT_OUTPUT = _HERE / "results" / "benchmark_report.json"


# ---------------------------------------------------------------------------
# Dynamic module loader
# ---------------------------------------------------------------------------

def _load_benchmark(module_name: str) -> Any:
    """Import a benchmark module from the ``benchmarks/`` directory."""
    module_path = _HERE / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot find benchmark module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_all(
    output_path: Path = DEFAULT_OUTPUT,
    training_repeats: int = 3,
    quiet: bool = False,
) -> dict[str, Any]:
    """Run every benchmark and return the consolidated report dict."""

    def _log(msg: str) -> None:
        if not quiet:
            print(msg)

    report: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor() or "unknown",
            "cpu_count": os.cpu_count(),
        },
        "benchmarks": [],
        "summary": {},
    }

    suite = [
        ("bench_training",  "Training Throughput",  {"repeats": training_repeats}),
        ("bench_inference", "Inference Latency",    {}),
        ("bench_memory",    "Memory Usage",         {}),
    ]

    total_start = time.perf_counter()

    for module_name, display_name, kwargs in suite:
        _log(f"\n{'─' * 60}")
        _log(f"▶  {display_name} …")
        t0 = time.perf_counter()
        try:
            mod = _load_benchmark(module_name)
            result = mod.run_benchmark(**kwargs)
            elapsed = round(time.perf_counter() - t0, 3)
            result["elapsed_sec"] = elapsed
            _log(f"   ✅  Done in {elapsed:.2f}s")
        except Exception as exc:  # noqa: BLE001
            elapsed = round(time.perf_counter() - t0, 3)
            result = {
                "benchmark": module_name,
                "status": "error",
                "error": str(exc),
                "elapsed_sec": elapsed,
            }
            _log(f"   ❌  Error: {exc}")

        report["benchmarks"].append(result)

    total_elapsed = round(time.perf_counter() - total_start, 3)

    # -----------------------------------------------------------------------
    # Build summary
    # -----------------------------------------------------------------------
    summary: dict[str, Any] = {"total_elapsed_sec": total_elapsed}

    for bench in report["benchmarks"]:
        name = bench.get("benchmark", "unknown")
        if bench.get("status") == "error":
            continue
        if name == "training_throughput":
            summary["training_mean_steps_per_sec"] = (
                bench["results"]["mean_steps_per_sec"]
            )
        elif name == "inference_latency":
            # Report p50 and p99 for batch-1
            b1 = bench["results"].get("batch_1", {})
            summary["inference_batch1_p50_ms"] = b1.get("p50_ms")
            summary["inference_batch1_p99_ms"] = b1.get("p99_ms")
        elif name == "memory_usage":
            summary["memory_overall_peak_mib"] = bench.get("overall_peak_mib")

    report["summary"] = summary

    # -----------------------------------------------------------------------
    # Write JSON report
    # -----------------------------------------------------------------------
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    _log(f"\n{'═' * 60}")
    _log(f"📄  Report written to: {output_path}")
    _log(f"⏱   Total elapsed: {total_elapsed:.2f}s")
    _log("")
    _log("Summary:")
    for k, v in summary.items():
        _log(f"  {k}: {v}")

    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run all _codex_ performance benchmarks.")
    p.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output JSON path (default: {DEFAULT_OUTPUT})",
    )
    p.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="Number of repeats for the training benchmark (default: 3)",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-benchmark progress output",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run_all(
        output_path=args.output,
        training_repeats=args.repeats,
        quiet=args.quiet,
    )
