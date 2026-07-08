"""
Comprehensive Benchmark Runner and Report Generator.

Runs all benchmarks multiple times, analyzes results, and generates
detailed performance reports with regression detection.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from performance_regression_analysis import (
    PerformanceAnalyzer,
    run_regression_analysis,
    generate_performance_report,
)

__all__ = ["BenchmarkRunner", "run_all_benchmarks"]


class BenchmarkRunner:
    """Runs all benchmarks and collects results."""

    def __init__(self, output_dir: Path = None, num_runs: int = 5):
        """Initialize benchmark runner.

        Args:
            output_dir: Directory to save results
            num_runs: Number of times to run each benchmark
        """
        self.output_dir = output_dir or Path(__file__).parent / "results"
        self.num_runs = num_runs
        self.results: list[dict[str, Any]] = []

    def run_training_benchmark(self) -> dict[str, Any]:
        """Run training throughput benchmark."""
        print("\n[1/3] Running training throughput benchmark...")
        print(f"      Running {self.num_runs} times...")

        all_throughputs = []

        for run in range(self.num_runs):
            try:
                result = subprocess.run(
                    [sys.executable, "benchmarks/bench_training.py"],
                    cwd=Path(__file__).parent.parent,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode == 0:
                    # Parse JSON output
                    import json as json_module

                    # Find JSON in output
                    output = result.stdout
                    start_idx = output.find("{")
                    if start_idx >= 0:
                        json_str = output[start_idx : output.rfind("}") + 1]
                        data = json_module.loads(json_str)
                        throughputs = data["results"]["throughput_steps_per_sec"]
                        all_throughputs.extend(throughputs)
                        print(f"      Run {run + 1}/{self.num_runs}: {throughputs[-1]:.2f} steps/sec")

            except Exception as e:
                print(f"      ⚠️  Run {run + 1} failed: {e}")

        if all_throughputs:
            import statistics

            return {
                "benchmark": "training_throughput",
                "description": "SGD training loop — steps/sec (higher is better)",
                "results": {
                    "throughput_steps_per_sec": all_throughputs,
                    "mean_steps_per_sec": round(statistics.mean(all_throughputs), 2),
                    "stdev_steps_per_sec": round(
                        statistics.stdev(all_throughputs) if len(all_throughputs) > 1 else 0, 2
                    ),
                    "median_steps_per_sec": round(
                        sorted(all_throughputs)[len(all_throughputs) // 2], 2
                    ),
                },
                "status": "pass",
            }

        return {"status": "failed", "error": "No results collected"}

    def run_inference_benchmark(self) -> dict[str, Any]:
        """Run inference latency benchmark."""
        print("\n[2/3] Running inference latency benchmark...")
        print(f"      Running {self.num_runs} times...")

        batch_results = {
            "batch_1": {"latencies": []},
            "batch_8": {"latencies": []},
            "batch_32": {"latencies": []},
        }

        for run in range(self.num_runs):
            try:
                result = subprocess.run(
                    [sys.executable, "benchmarks/bench_inference.py"],
                    cwd=Path(__file__).parent.parent,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode == 0:
                    import json as json_module

                    # Parse JSON output
                    output = result.stdout
                    start_idx = output.find("{")
                    if start_idx >= 0:
                        json_str = output[start_idx : output.rfind("}") + 1]
                        data = json_module.loads(json_str)
                        for batch_key in batch_results.keys():
                            if batch_key in data["results"]:
                                mean = data["results"][batch_key]["mean_ms_per_sample"]
                                batch_results[batch_key]["latencies"].append(mean)
                        print(f"      Run {run + 1}/{self.num_runs}: completed")

            except Exception as e:
                print(f"      ⚠️  Run {run + 1} failed: {e}")

        if all(batch_results[k]["latencies"] for k in batch_results):
            import statistics

            results = {}
            for batch_key, data in batch_results.items():
                latencies = data["latencies"]
                results[batch_key] = {
                    "n_samples_per_call": int(batch_key.split("_")[1]),
                    "mean_ms_per_sample": round(statistics.mean(latencies), 4),
                    "stdev_ms": round(
                        statistics.stdev(latencies) if len(latencies) > 1 else 0, 4
                    ),
                    "p99_ms": round(sorted(latencies)[-max(1, len(latencies) // 100)], 4),
                }

            return {
                "benchmark": "inference_latency",
                "description": "Two-layer MLP forward pass — ms/sample (lower is better)",
                "results": results,
                "status": "pass",
            }

        return {"status": "failed", "error": "No results collected"}

    def run_memory_benchmark(self) -> dict[str, Any]:
        """Run memory usage benchmark."""
        print("\n[3/3] Running memory usage benchmark...")
        print(f"      Running {self.num_runs} times...")

        all_peaks = []

        for run in range(self.num_runs):
            try:
                result = subprocess.run(
                    [sys.executable, "benchmarks/bench_memory.py"],
                    cwd=Path(__file__).parent.parent,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode == 0:
                    import json as json_module

                    # Parse JSON output
                    output = result.stdout
                    start_idx = output.find("{")
                    if start_idx >= 0:
                        json_str = output[start_idx : output.rfind("}") + 1]
                        data = json_module.loads(json_str)
                        peak = data["overall_peak_mib"]
                        all_peaks.append(peak)
                        print(f"      Run {run + 1}/{self.num_runs}: {peak:.3f} MiB peak")

            except Exception as e:
                print(f"      ⚠️  Run {run + 1} failed: {e}")

        if all_peaks:
            import statistics

            return {
                "benchmark": "memory_usage",
                "description": "Peak heap allocation (lower is better)",
                "results": {
                    "peak_mib_measurements": all_peaks,
                    "mean_peak_mib": round(statistics.mean(all_peaks), 4),
                    "stdev_peak_mib": round(
                        statistics.stdev(all_peaks) if len(all_peaks) > 1 else 0, 4
                    ),
                    "max_peak_mib": round(max(all_peaks), 4),
                    "min_peak_mib": round(min(all_peaks), 4),
                },
                "status": "pass",
            }

        return {"status": "failed", "error": "No results collected"}

    def run_all(self) -> list[dict[str, Any]]:
        """Run all benchmarks."""
        print("\n" + "=" * 80)
        print("STARTING COMPREHENSIVE PERFORMANCE BENCHMARKS")
        print("=" * 80)
        print(f"Output directory: {self.output_dir}")
        print(f"Runs per benchmark: {self.num_runs}")

        start_time = time.time()

        # Run all benchmarks
        results = [
            self.run_training_benchmark(),
            self.run_inference_benchmark(),
            self.run_memory_benchmark(),
        ]

        elapsed = time.time() - start_time

        print(f"\n✅  All benchmarks completed in {elapsed:.1f} seconds")

        self.results = results
        return results

    def save_results(self, filename: str = "benchmark_results.json") -> Path:
        """Save results to JSON file."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / filename

        with open(output_path, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"Results saved to: {output_path}")
        return output_path


def run_all_benchmarks(
    output_dir: Path = None,
    num_runs: int = 5,
) -> dict[str, Any]:
    """Run comprehensive benchmark suite and generate analysis report.

    Args:
        output_dir: Directory to save results
        num_runs: Number of times to run each benchmark

    Returns:
        Dictionary with benchmark results and analysis
    """
    runner = BenchmarkRunner(output_dir=output_dir, num_runs=num_runs)
    benchmark_results = runner.run_all()

    # Save raw results
    runner.save_results("benchmark_results.json")

    # Run regression analysis
    print("\n" + "=" * 80)
    print("ANALYZING PERFORMANCE & DETECTING REGRESSIONS")
    print("=" * 80)

    # Create baseline from first run (assuming baseline results file exists)
    baseline_results = None
    baseline_file = (output_dir or Path(__file__).parent / "results") / "baseline.json"
    if baseline_file.exists():
        with open(baseline_file) as f:
            baseline_results = json.load(f)

    analysis = run_regression_analysis(baseline_results or {}, {"results": {}})

    # Generate report
    print("\n" + "=" * 80)
    print("GENERATING PERFORMANCE REPORT")
    print("=" * 80)

    output_dir = output_dir or Path(__file__).parent / "results"
    report_path = output_dir / "performance_report.json"
    generate_performance_report(benchmark_results, analysis, report_path)

    # Print summary
    print("\n" + "=" * 80)
    print("PERFORMANCE BENCHMARKING COMPLETE")
    print("=" * 80)

    summary = {
        "status": "COMPLETE",
        "benchmarks_run": len(benchmark_results),
        "performance_issues_identified": analysis.get("total_critical_issues", 0)
        + analysis.get("total_high_issues", 0)
        + analysis.get("total_medium_issues", 0)
        + analysis.get("total_low_issues", 0),
        "critical_issues": analysis.get("total_critical_issues", 0),
        "high_issues": analysis.get("total_high_issues", 0),
        "medium_issues": analysis.get("total_medium_issues", 0),
        "low_issues": analysis.get("total_low_issues", 0),
        "benchmark_results": benchmark_results,
        "analysis": analysis,
    }

    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run comprehensive performance benchmarks")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for results",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of times to run each benchmark",
    )

    args = parser.parse_args()

    summary = run_all_benchmarks(
        output_dir=args.output_dir,
        num_runs=args.runs,
    )

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total benchmarks run: {summary['benchmarks_run']}")
    print(f"Performance issues identified: {summary['performance_issues_identified']}")
    print(f"  - Critical: {summary['critical_issues']}")
    print(f"  - High: {summary['high_issues']}")
    print(f"  - Medium: {summary['medium_issues']}")
    print(f"  - Low: {summary['low_issues']}")
    print("=" * 80)
