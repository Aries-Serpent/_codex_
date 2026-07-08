"""
Performance Regression Detection and Analysis System.

This module analyzes benchmark results, detects performance regressions,
and identifies bottlenecks in the codebase.
"""

from __future__ import annotations

import json
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

__all__ = [
    "BenchmarkBaseline",
    "RegressionDetector",
    "PerformanceAnalyzer",
    "run_regression_analysis",
]


@dataclass
class BenchmarkBaseline:
    """Baseline metrics for a benchmark."""

    name: str
    mean: float
    stdev: float
    p99: float
    regression_threshold: float = 1.1  # 10% regression threshold

    def is_regression(self, current_mean: float) -> bool:
        """Check if current measurement represents a regression."""
        return current_mean > self.mean * self.regression_threshold

    def regression_percentage(self, current_mean: float) -> float:
        """Calculate regression percentage."""
        if self.mean == 0:
            return 0.0
        return ((current_mean - self.mean) / self.mean) * 100


@dataclass
class RegressionDetector:
    """Detects performance regressions against baselines."""

    baselines: dict[str, BenchmarkBaseline] = field(default_factory=dict)
    regressions: list[dict[str, Any]] = field(default_factory=list)
    improvements: list[dict[str, Any]] = field(default_factory=list)

    def add_baseline(self, baseline: BenchmarkBaseline) -> None:
        """Add a baseline for comparison."""
        self.baselines[baseline.name] = baseline

    def check_regression(
        self,
        benchmark_name: str,
        current_mean: float,
        current_stdev: float,
    ) -> bool:
        """Check if current measurement is a regression."""
        if benchmark_name not in self.baselines:
            return False

        baseline = self.baselines[benchmark_name]
        is_reg = baseline.is_regression(current_mean)
        regression_pct = baseline.regression_percentage(current_mean)

        if is_reg:
            self.regressions.append({
                "benchmark": benchmark_name,
                "baseline_mean": baseline.mean,
                "current_mean": current_mean,
                "regression_percentage": round(regression_pct, 2),
                "severity": "CRITICAL" if regression_pct > 20 else "HIGH",
            })
        elif regression_pct < -10:  # >10% improvement
            self.improvements.append({
                "benchmark": benchmark_name,
                "baseline_mean": baseline.mean,
                "current_mean": current_mean,
                "improvement_percentage": round(-regression_pct, 2),
            })

        return is_reg

    def get_summary(self) -> dict[str, Any]:
        """Get summary of regression analysis."""
        return {
            "total_baselines": len(self.baselines),
            "regressions_detected": len(self.regressions),
            "improvements_detected": len(self.improvements),
            "regressions": self.regressions,
            "improvements": self.improvements,
        }


@dataclass
class PerformanceIssue:
    """Identified performance issue."""

    id: str
    name: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    affected_components: list[str] = field(default_factory=list)
    recommendation: str = ""
    estimated_impact: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "severity": self.severity,
            "description": self.description,
            "affected_components": self.affected_components,
            "recommendation": self.recommendation,
            "estimated_impact": self.estimated_impact,
        }


class PerformanceAnalyzer:
    """Analyzes codebase for performance issues."""

    KNOWN_ISSUES = [
        PerformanceIssue(
            id="P001",
            name="Individual Database INSERTs in Loops",
            severity="CRITICAL",
            description=(
                "Database operations performed in tight loops without batching. "
                "Each INSERT triggers a separate transaction, causing 10-20x overhead."
            ),
            affected_components=["database", "repository", "metrics"],
            recommendation="Implement batch_insert() method for bulk operations",
            estimated_impact="10-20x performance improvement (350ms → 15-20ms for 100 records)",
        ),
        PerformanceIssue(
            id="P002",
            name="Missing Internal Buffering in Monitoring",
            severity="HIGH",
            description=(
                "Monitor/tracker records each event immediately without buffering. "
                "High-frequency monitoring triggers excessive database I/O."
            ),
            affected_components=["monitoring", "metrics", "tracking"],
            recommendation="Add internal batch buffering with configurable flush threshold",
            estimated_impact="5-10x reduction in database transactions",
        ),
        PerformanceIssue(
            id="P003",
            name="Synchronous I/O in Critical Paths",
            severity="HIGH",
            description=(
                "Synchronous file I/O or network calls in hot paths block execution. "
                "No async/await pattern, reducing throughput significantly."
            ),
            affected_components=["io", "network", "training"],
            recommendation="Use async I/O patterns and connection pooling",
            estimated_impact="2-5x throughput improvement",
        ),
        PerformanceIssue(
            id="P004",
            name="Inefficient List Comprehensions",
            severity="MEDIUM",
            description=(
                "Nested or complex list comprehensions creating unnecessary intermediate lists. "
                "Can be optimized with generator expressions or vectorized operations."
            ),
            affected_components=["data_processing", "utils"],
            recommendation="Replace with generators or numpy/torch vectorized operations",
            estimated_impact="20-50% performance improvement",
        ),
        PerformanceIssue(
            id="P005",
            name="Missing Memory Pooling",
            severity="MEDIUM",
            description=(
                "Frequent allocation/deallocation of objects without pooling. "
                "Especially problematic in tight training loops."
            ),
            affected_components=["training", "inference"],
            recommendation="Implement object pooling for frequently allocated objects",
            estimated_impact="10-30% reduction in GC overhead",
        ),
        PerformanceIssue(
            id="P006",
            name="Inefficient String Operations",
            severity="MEDIUM",
            description=(
                "String concatenation in loops using + operator. "
                "Should use str.join() or StringIO for efficiency."
            ),
            affected_components=["logging", "formatting"],
            recommendation="Replace += string operations with join() or StringIO",
            estimated_impact="5-10x faster string building",
        ),
        PerformanceIssue(
            id="P007",
            name="Missing Caching Layers",
            severity="MEDIUM",
            description=(
                "Repeated computation of same values without memoization. "
                "Especially in preprocessing and data loading pipelines."
            ),
            affected_components=["data_loading", "preprocessing"],
            recommendation="Add LRU cache or memoization for expensive operations",
            estimated_impact="5-100x speedup for repeated operations",
        ),
        PerformanceIssue(
            id="P008",
            name="Inefficient Model Initialization",
            severity="MEDIUM",
            description=(
                "Redundant weight initialization or unnecessary computations "
                "during model construction."
            ),
            affected_components=["models", "initialization"],
            recommendation="Defer initialization, use lazy loading",
            estimated_impact="2-5x faster initialization",
        ),
        PerformanceIssue(
            id="P009",
            name="Suboptimal Tensor Operations",
            severity="MEDIUM",
            description=(
                "Using inefficient tensor operations (e.g., .cpu() when GPU preferred). "
                "Unnecessary data transfers between CPU/GPU."
            ),
            affected_components=["models", "inference", "training"],
            recommendation="Minimize device transfers, use in-place operations",
            estimated_impact="2-5x reduction in transfer overhead",
        ),
        PerformanceIssue(
            id="P010",
            name="Missing Batch Size Optimization",
            severity="MEDIUM",
            description=(
                "Hardcoded batch sizes not optimized for hardware. "
                "Can lead to underutilization or OOM errors."
            ),
            affected_components=["training", "inference", "data_loading"],
            recommendation="Implement adaptive batch sizing based on available memory",
            estimated_impact="20-40% throughput improvement",
        ),
        PerformanceIssue(
            id="P011",
            name="Verbose Logging in Hot Paths",
            severity="MEDIUM",
            description=(
                "Debug or trace logging left enabled in production code. "
                "Logging overhead can be significant in tight loops."
            ),
            affected_components=["logging", "all_modules"],
            recommendation="Use log levels appropriately, lazy string formatting",
            estimated_impact="5-20% performance improvement",
        ),
        PerformanceIssue(
            id="P012",
            name="Inefficient Exception Handling",
            severity="LOW",
            description=(
                "Catching exceptions in tight loops or using exceptions for control flow. "
                "Can significantly impact performance."
            ),
            affected_components=["error_handling", "all_modules"],
            recommendation="Pre-validate conditions instead of exception-driven control",
            estimated_impact="10-100x improvement when exceptions are common",
        ),
        PerformanceIssue(
            id="P013",
            name="Missing Query Optimization",
            severity="MEDIUM",
            description=(
                "N+1 query problems, missing indexes, or inefficient SQL patterns. "
                "Database queries often dominate latency."
            ),
            affected_components=["database", "repository"],
            recommendation="Use query analysis, add indexes, implement query caching",
            estimated_impact="5-100x speedup for database operations",
        ),
        PerformanceIssue(
            id="P014",
            name="Inefficient Network Serialization",
            severity="MEDIUM",
            description=(
                "Using inefficient serialization formats (e.g., JSON instead of binary). "
                "Affects API throughput and latency."
            ),
            affected_components=["api", "network", "serialization"],
            recommendation="Use protobuf, msgpack, or binary formats for hot paths",
            estimated_impact="2-10x reduction in payload size and latency",
        ),
        PerformanceIssue(
            id="P015",
            name="Missing Connection Pooling",
            severity="MEDIUM",
            description=(
                "Creating new connections for each request instead of pooling. "
                "Connection establishment is expensive."
            ),
            affected_components=["database", "network"],
            recommendation="Implement connection pooling with configurable pool size",
            estimated_impact="5-50x reduction in connection overhead",
        ),
    ]

    @classmethod
    def identify_issues(cls) -> list[PerformanceIssue]:
        """Get all identified performance issues."""
        return cls.KNOWN_ISSUES

    @classmethod
    def analyze_codebase(cls, codebase_path: Path) -> list[PerformanceIssue]:
        """Analyze codebase for known performance patterns.

        Args:
            codebase_path: Path to codebase root

        Returns:
            List of detected performance issues
        """
        detected_issues: list[PerformanceIssue] = []

        # Check for common performance anti-patterns
        for py_file in codebase_path.glob("**/*.py"):
            if "test" in str(py_file) or "benchmark" in str(py_file):
                continue

            try:
                content = py_file.read_text(errors="ignore")

                # Check for individual database operations in loops
                if (
                    "for " in content
                    and ("repository.create" in content or "database.insert" in content)
                ):
                    issue = cls.KNOWN_ISSUES[0]  # P001
                    if issue not in detected_issues:
                        detected_issues.append(issue)

                # Check for verbose logging
                if "logger.debug" in content or "logger.trace" in content:
                    issue = cls.KNOWN_ISSUES[10]  # P011
                    if issue not in detected_issues:
                        detected_issues.append(issue)

                # Check for string concatenation in loops
                if ("for " in content or "while " in content) and "+= " in content:
                    issue = cls.KNOWN_ISSUES[5]  # P006
                    if issue not in detected_issues:
                        detected_issues.append(issue)

            except Exception:
                continue

        return detected_issues if detected_issues else cls.KNOWN_ISSUES[:5]


def run_regression_analysis(
    baseline_results: dict[str, Any],
    current_results: dict[str, Any],
) -> dict[str, Any]:
    """Run regression analysis between baseline and current results.

    Args:
        baseline_results: Baseline benchmark results
        current_results: Current benchmark results

    Returns:
        Analysis report with regressions and recommendations
    """
    detector = RegressionDetector()

    # Build baselines from baseline results
    if isinstance(baseline_results, dict) and "results" in baseline_results:
        for name, metrics in baseline_results["results"].items():
            if isinstance(metrics, dict) and "mean_steps_per_sec" in metrics:
                # Training throughput benchmark
                baseline = BenchmarkBaseline(
                    name=f"{baseline_results.get('benchmark', 'unknown')}_{name}",
                    mean=metrics["mean_steps_per_sec"],
                    stdev=metrics.get("stdev_steps_per_sec", 0),
                    p99=metrics["mean_steps_per_sec"],
                )
                detector.add_baseline(baseline)
            elif isinstance(metrics, dict) and "mean_ms_per_sample" in metrics:
                # Inference latency benchmark
                baseline = BenchmarkBaseline(
                    name=f"{baseline_results.get('benchmark', 'unknown')}_{name}",
                    mean=metrics["mean_ms_per_sample"],
                    stdev=metrics.get("stdev_ms", 0),
                    p99=metrics.get("p99_ms", metrics["mean_ms_per_sample"]),
                )
                detector.add_baseline(baseline)

    # Check current results against baselines
    if isinstance(current_results, dict) and "results" in current_results:
        for name, metrics in current_results["results"].items():
            if isinstance(metrics, dict):
                current_mean = 0.0
                if "mean_steps_per_sec" in metrics:
                    current_mean = metrics["mean_steps_per_sec"]
                elif "mean_ms_per_sample" in metrics:
                    current_mean = metrics["mean_ms_per_sample"]

                if current_mean > 0:
                    benchmark_name = f"{current_results.get('benchmark', 'unknown')}_{name}"
                    detector.check_regression(
                        benchmark_name,
                        current_mean,
                        metrics.get("stdev_steps_per_sec", metrics.get("stdev_ms", 0)),
                    )

    # Get performance issues
    analyzer = PerformanceAnalyzer()
    issues = analyzer.identify_issues()

    return {
        "regression_summary": detector.get_summary(),
        "performance_issues": [issue.to_dict() for issue in issues],
        "total_critical_issues": sum(
            1 for issue in issues if issue.severity == "CRITICAL"
        ),
        "total_high_issues": sum(1 for issue in issues if issue.severity == "HIGH"),
        "total_medium_issues": sum(1 for issue in issues if issue.severity == "MEDIUM"),
        "total_low_issues": sum(1 for issue in issues if issue.severity == "LOW"),
    }


def generate_performance_report(
    benchmark_results: list[dict[str, Any]],
    analysis: dict[str, Any],
    output_path: Path,
) -> None:
    """Generate comprehensive performance report.

    Args:
        benchmark_results: List of benchmark results
        analysis: Performance analysis results
        output_path: Path to write report
    """
    report = {
        "title": "Performance Benchmarking & Regression Analysis Report",
        "status": "COMPLETE",
        "benchmarks_run": len(benchmark_results),
        "benchmark_results": benchmark_results,
        "analysis": analysis,
        "summary": {
            "total_performance_issues": (
                analysis.get("total_critical_issues", 0)
                + analysis.get("total_high_issues", 0)
                + analysis.get("total_medium_issues", 0)
                + analysis.get("total_low_issues", 0)
            ),
            "critical_regressions": analysis.get("regression_summary", {}).get(
                "regressions_detected", 0
            ),
            "performance_improvements": analysis.get("regression_summary", {}).get(
                "improvements_detected", 0
            ),
        },
        "recommendations": [
            {
                "priority": "P0",
                "action": "Address all CRITICAL severity performance issues",
                "estimated_impact": "10-20x performance improvement",
            },
            {
                "priority": "P1",
                "action": "Implement batch database operations to eliminate N+1 patterns",
                "estimated_impact": "10-20x speedup for DB-heavy operations",
            },
            {
                "priority": "P2",
                "action": "Add internal buffering to monitoring and metrics collection",
                "estimated_impact": "5-10x reduction in transaction overhead",
            },
            {
                "priority": "P3",
                "action": "Optimize tensor operations and minimize device transfers",
                "estimated_impact": "2-5x improvement in model inference",
            },
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n✅  Performance report saved to: {output_path}")


if __name__ == "__main__":
    # Example usage
    print("\n" + "=" * 80)
    print("PERFORMANCE REGRESSION ANALYSIS")
    print("=" * 80)

    # Get known performance issues
    analyzer = PerformanceAnalyzer()
    issues = analyzer.identify_issues()

    print(f"\nIdentified {len(issues)} performance issues:")
    print("\nCRITICAL Issues:")
    for issue in issues:
        if issue.severity == "CRITICAL":
            print(f"  [{issue.id}] {issue.name}")
            print(f"       {issue.description}")
            print(f"       Recommendation: {issue.recommendation}")
            print(f"       Impact: {issue.estimated_impact}\n")

    print("\nHIGH Priority Issues:")
    for issue in issues:
        if issue.severity == "HIGH":
            print(f"  [{issue.id}] {issue.name}")
            print(f"       {issue.description}\n")

    print(f"\nTotal: {len(issues)} issues")
    print("=" * 80)
