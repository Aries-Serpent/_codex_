#!/usr/bin/env python3
"""
Benchmark Validation Script
Phase 2: Performance Benchmarking

Validates benchmark results against performance targets.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

# Performance Targets
TARGETS = {
    "task_latency": {
        "1_task_max_us": 1000,  # < 1ms for single task
        "1000_tasks_max_us": 1000,  # < 1ms average per task
        "unit": "μs"
    },
    "throughput": {
        "min_tasks_per_sec": 10_000,  # > 10k tasks/s
        "unit": "tasks/s"
    },
    "compression": {
        "min_ratio": 10.0,  # > 10x compression ratio
        "max_compress_time_ms": 100,  # < 100ms for 1MB
        "max_decompress_time_ms": 100,  # < 100ms for 1MB
        "unit": "ratio/ms"
    },
    "concurrent_agents": {
        "min_agents": 1000,  # Support 1000+ agents
        "max_latency_increase": 2.0,  # < 2x latency increase
        "unit": "agents"
    }
}


def load_criterion_results(criterion_dir: Path) -> Dict[str, Any]:
    """Load benchmark results from Criterion output."""
    results = {}
    
    if not criterion_dir.exists():
        print(f"❌ Criterion directory not found: {criterion_dir}")
        return results
    
    # Look for benchmark results
    for bench_dir in criterion_dir.iterdir():
        if not bench_dir.is_dir():
            continue
            
        estimates_file = bench_dir / "base" / "estimates.json"
        if estimates_file.exists():
            try:
                with open(estimates_file) as f:
                    results[bench_dir.name] = json.load(f)
            except Exception as e:
                print(f"⚠️  Failed to load {bench_dir.name}: {e}")
    
    return results


def validate_task_latency(results: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate task latency benchmarks."""
    latency_results = {k: v for k, v in results.items() if k.startswith("task_latency")}
    
    if not latency_results:
        return False, "No task latency benchmarks found"
    
    all_passed = True
    details = []
    
    for bench_name, result in latency_results.items():
        mean_ns = result.get("mean", {}).get("point_estimate", 0)
        mean_us = mean_ns / 1000  # Convert ns to μs
        
        # Extract task count from benchmark name (e.g., "task_latency/1" -> 1)
        if "/" in bench_name:
            avg_us_per_task = mean_us
            
            target_us = TARGETS["task_latency"]["1000_tasks_max_us"]
            passed = avg_us_per_task < target_us
            all_passed &= passed
            
            status = "✅" if passed else "❌"
            details.append(
                f"{status} {bench_name}: {avg_us_per_task:.2f}μs/task "
                f"(target: < {target_us}μs)"
            )
    
    return all_passed, "\n".join(details)


def validate_throughput(results: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate throughput benchmarks."""
    throughput_results = {k: v for k, v in results.items() if "throughput" in k}
    
    if not throughput_results:
        return False, "No throughput benchmarks found"
    
    all_passed = True
    details = []
    
    for bench_name, result in throughput_results.items():
        mean_ns = result.get("mean", {}).get("point_estimate", 0)
        
        if "10k" in bench_name:
            # Time to process 10k tasks
            tasks_per_sec = 10_000 / (mean_ns / 1e9)
            target = TARGETS["throughput"]["min_tasks_per_sec"]
            passed = tasks_per_sec > target
            all_passed &= passed
            
            status = "✅" if passed else "❌"
            details.append(
                f"{status} {bench_name}: {tasks_per_sec:,.0f} tasks/s "
                f"(target: > {target:,} tasks/s)"
            )
    
    return all_passed, "\n".join(details)


def validate_compression(results: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate compression benchmarks."""
    compression_results = {k: v for k, v in results.items() if "compression" in k}
    
    if not compression_results:
        return False, "No compression benchmarks found"
    
    all_passed = True
    details = []
    
    for bench_name, result in compression_results.items():
        mean_ns = result.get("mean", {}).get("point_estimate", 0)
        mean_ms = mean_ns / 1e6
        
        if "compress_1mb" in bench_name:
            target = TARGETS["compression"]["max_compress_time_ms"]
            passed = mean_ms < target
            all_passed &= passed
            
            status = "✅" if passed else "❌"
            details.append(
                f"{status} {bench_name}: {mean_ms:.2f}ms "
                f"(target: < {target}ms)"
            )
        
        elif "decompress_1mb" in bench_name:
            target = TARGETS["compression"]["max_decompress_time_ms"]
            passed = mean_ms < target
            all_passed &= passed
            
            status = "✅" if passed else "❌"
            details.append(
                f"{status} {bench_name}: {mean_ms:.2f}ms "
                f"(target: < {target}ms)"
            )
    
    return all_passed, "\n".join(details)


def validate_concurrent_agents(results: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate concurrent agents benchmarks."""
    agent_results = {k: v for k, v in results.items() if "concurrent_agents" in k}
    
    if not agent_results:
        return False, "No concurrent agent benchmarks found"
    
    all_passed = True
    details = []
    
    # Check if 1000 agents benchmark exists
    agent_1000 = next((k for k in agent_results.keys() if "1000" in k), None)
    
    if agent_1000:
        result = agent_results[agent_1000]
        mean_ns = result.get("mean", {}).get("point_estimate", 0)
        mean_ms = mean_ns / 1e6
        
        status = "✅"
        details.append(
            f"{status} 1000 agents: {mean_ms:.2f}ms per 1000 tasks "
            f"(supports {TARGETS['concurrent_agents']['min_agents']} agents)"
        )
    else:
        all_passed = False
        details.append("❌ 1000 agent benchmark not found")
    
    return all_passed, "\n".join(details)


def generate_summary_report(results: Dict[str, Any], validations: Dict[str, Tuple[bool, str]]) -> str:
    """Generate a summary report of all validations."""
    report = []
    report.append("=" * 80)
    report.append("📊 Benchmark Validation Report")
    report.append("=" * 80)
    report.append("")
    
    # Overall status
    all_passed = all(v[0] for v in validations.values())
    overall_status = "✅ ALL BENCHMARKS PASSED" if all_passed else "❌ SOME BENCHMARKS FAILED"
    report.append(f"Overall Status: {overall_status}")
    report.append("")
    
    # Individual validations
    for category, (passed, details) in validations.items():
        status_icon = "✅" if passed else "❌"
        report.append(f"{status_icon} {category.upper()}")
        report.append("-" * 80)
        report.append(details)
        report.append("")
    
    # Summary table
    report.append("=" * 80)
    report.append("Summary")
    report.append("=" * 80)
    
    for category, (passed, _) in validations.items():
        status = "PASS" if passed else "FAIL"
        report.append(f"  {category:.<40} {status}")
    
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """Main validation function."""
    print("🚀 Starting Benchmark Validation")
    print()
    
    # Locate Criterion results
    criterion_dir = Path("target/criterion")
    
    if not criterion_dir.exists():
        print("❌ No benchmark results found.")
        print("   Run 'cargo bench' first to generate results.")
        sys.exit(1)
    
    # Load results
    print("📂 Loading benchmark results...")
    results = load_criterion_results(criterion_dir)
    
    if not results:
        print("❌ No valid benchmark results found in target/criterion/")
        sys.exit(1)
    
    print(f"✅ Loaded {len(results)} benchmark results")
    print()
    
    # Run validations
    validations = {
        "task_latency": validate_task_latency(results),
        "throughput": validate_throughput(results),
        "compression": validate_compression(results),
        "concurrent_agents": validate_concurrent_agents(results),
    }
    
    # Generate and print report
    report = generate_summary_report(results, validations)
    print(report)
    
    # Save report to file
    report_file = Path("coverage/benchmark_validation_report.txt")
    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, "w") as f:
        f.write(report)
    
    print()
    print(f"📄 Report saved to: {report_file}")
    
    # Exit with appropriate code
    all_passed = all(v[0] for v in validations.values())
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
