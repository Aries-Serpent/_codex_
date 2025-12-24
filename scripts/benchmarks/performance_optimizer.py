#!/usr/bin/env python
"""Automated Performance Optimization Benchmarking

Agent-driven performance benchmarking for MLOps features.
Identifies bottlenecks and generates optimization recommendations.

Usage:
    python scripts/benchmarks/performance_optimizer.py --all
    python scripts/benchmarks/performance_optimizer.py --feature mlflow

Agent Integration:
    from scripts.benchmarks.performance_optimizer import PerformanceOptimizer
    optimizer = PerformanceOptimizer()
    results = optimizer.run_all_benchmarks()
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
import statistics

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """Agent-driven performance optimizer for ML Ops features."""

    def __init__(self, iterations: int = 100, base_path: Path = None):
        self.iterations = iterations
        self.base_path = base_path or Path.cwd()

    def benchmark_function(
        self, func: Callable, name: str, iterations: int = None
    ) -> dict[str, Any]:
        """Benchmark a function and return performance metrics.

        Args:
            func: Function to benchmark
            name: Benchmark name
            iterations: Number of iterations (default: self.iterations)

        Returns:
            dict with performance metrics
        """
        iterations = iterations or self.iterations
        times = []

        logger.info(f"Benchmarking {name} ({iterations} iterations)")

        for i in range(iterations):
            start = time.perf_counter()
            try:
                func()
                elapsed = (time.perf_counter() - start) * 1000  # ms
                times.append(elapsed)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.debug(f"Benchmark iteration {i} failed: {e}")
                continue

        if not times:
            return {"name": name, "status": "failed", "error": "All iterations failed"}

        times.sort()
        n = len(times)

        return {
            "name": name,
            "status": "success",
            "iterations": n,
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "stddev_ms": statistics.stdev(times) if n > 1 else 0,
            "min_ms": min(times),
            "max_ms": max(times),
            "p50_ms": times[int(n * 0.50)],
            "p95_ms": times[int(n * 0.95)],
            "p99_ms": times[int(n * 0.99)],
        }

    def benchmark_mlflow_logging(self) -> dict[str, Any]:
        """Benchmark MLflow metric logging performance."""
        try:
            import mlflow

            mlflow.set_tracking_uri("file://./mlruns")

            def log_metrics():
                with mlflow.start_run(run_name="benchmark"):
                    mlflow.log_metrics({"test_metric": 0.5})

            result = self.benchmark_function(log_metrics, "mlflow_logging", 50)

            # Check against target (<5ms p95)
            if result["status"] == "success":
                result["meets_target"] = result["p95_ms"] < 5.0
                result["target_p95_ms"] = 5.0

                if not result["meets_target"]:
                    result["recommendation"] = "Enable async logging to reduce overhead"

            return result

        except ImportError as e:
            logger.debug(f"ImportError: {e}")
            return {"name": "mlflow_logging", "status": "skipped", "reason": "MLflow not available"}
        except Exception as e:
            logger.debug(f"Exception: {e}")
            return {"name": "mlflow_logging", "status": "error", "error": str(e)}

    def benchmark_feature_retrieval(self) -> dict[str, Any]:
        """Benchmark feature store retrieval performance."""
        try:
            from src.codex_ml.features.feature_store import FeatureStore

            fs_path = self.base_path / "artifacts/features/production"
            store = FeatureStore(str(fs_path))

            # Get first registered feature for testing
            features = store.list_features()
            if not features:
                return {
                    "name": "feature_retrieval",
                    "status": "skipped",
                    "reason": "No features registered",
                }

            test_feature = features[0]

            def retrieve_feature():
                store.get(test_feature.name, test_feature.version)

            result = self.benchmark_function(retrieve_feature, "feature_retrieval")

            # Check against target (<10ms p95)
            if result["status"] == "success":
                result["meets_target"] = result["p95_ms"] < 10.0
                result["target_p95_ms"] = 10.0

                if not result["meets_target"]:
                    result["recommendation"] = "Enable caching or partitioning to improve latency"

            return result

        except Exception as e:
            logger.debug(f"Exception: {e}")
            return {"name": "feature_retrieval", "status": "error", "error": str(e)}

    def benchmark_validation_overhead(self) -> dict[str, Any]:
        """Benchmark data validation overhead."""
        try:
            import pandas as pd
            import numpy as np

            # Create sample dataset
            data = pd.DataFrame(
                {
                    "feature_1": np.random.randn(10000),
                    "feature_2": np.random.randn(10000),
                    "label": np.random.randint(0, 2, 10000),
                }
            )

            def validate_data():
                # Simple validation checks
                assert not data.isnull().any().any()
                assert len(data) > 0
                assert "label" in data.columns

            result = self.benchmark_function(validate_data, "validation_overhead", 50)

            # Check against target (<5% overhead)
            if result["status"] == "success":
                result["meets_target"] = result["mean_ms"] < 50.0  # <5% of typical 1s operation
                result["target_mean_ms"] = 50.0

                if not result["meets_target"]:
                    result["recommendation"] = "Enable sampling or reduce validation checks"

            return result

        except Exception as e:
            logger.debug(f"Exception: {e}")
            return {"name": "validation_overhead", "status": "error", "error": str(e)}

    def benchmark_config_loading(self) -> dict[str, Any]:
        """Benchmark configuration loading performance."""
        try:
            import yaml

            config_path = self.base_path / "configs/production/tracking.yaml"

            def load_config():
                with open(config_path) as f:
                    yaml.safe_load(f)

            result = self.benchmark_function(load_config, "config_loading")

            # Check against target (<1ms p95)
            if result["status"] == "success":
                result["meets_target"] = result["p95_ms"] < 1.0
                result["target_p95_ms"] = 1.0

                if not result["meets_target"]:
                    result["recommendation"] = "Consider config caching"

            return result

        except Exception as e:
            logger.debug(f"Exception: {e}")
            return {"name": "config_loading", "status": "error", "error": str(e)}

    def run_all_benchmarks(self) -> dict[str, Any]:
        """Run all performance benchmarks.

        Returns:
            Complete benchmark report with recommendations
        """
        logger.info("Starting performance optimization benchmarks")

        report = {
            "timestamp": datetime.now().isoformat(),
            "iterations": self.iterations,
            "benchmarks": {
                "mlflow_logging": self.benchmark_mlflow_logging(),
                "feature_retrieval": self.benchmark_feature_retrieval(),
                "validation_overhead": self.benchmark_validation_overhead(),
                "config_loading": self.benchmark_config_loading(),
            },
        }

        # Analyze results
        successful = sum(1 for b in report["benchmarks"].values() if b["status"] == "success")
        total = len(report["benchmarks"])

        report["summary"] = {
            "total_benchmarks": total,
            "successful": successful,
            "failed": total - successful,
            "all_targets_met": all(
                b.get("meets_target", True)
                for b in report["benchmarks"].values()
                if b["status"] == "success"
            ),
        }

        # Generate agent recommendations
        report["agent_recommendations"] = self._generate_recommendations(report)

        return report

    def _generate_recommendations(self, report: dict[str, Any]) -> list[str]:
        """Generate optimization recommendations for agents.

        Args:
            report: Complete benchmark report

        Returns:
            list of actionable recommendations
        """
        recommendations = []

        benchmarks = report["benchmarks"]

        for name, result in benchmarks.items():
            if result["status"] == "success" and not result.get("meets_target", True):
                rec = result.get("recommendation")
                if rec:
                    recommendations.append(f"OPTIMIZE_{name.upper()}: {rec}")

        if report["summary"]["all_targets_met"]:
            recommendations.append("STATUS: All performance targets met. No optimization required.")

        if not recommendations:
            recommendations.append("STATUS: Benchmarks completed. Review individual results.")

        return recommendations

    def export_json(self, output_path: str = None) -> str:
        """Export benchmark results to JSON.

        Args:
            output_path: Output file path (optional)

        Returns:
            Path to exported file
        """
        results = self.run_all_benchmarks()

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"performance_benchmark_{timestamp}.json"

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Benchmark results exported to: {output_file}")
        return str(output_file)


def main():
    """CLI entry point for agent execution."""
    parser = argparse.ArgumentParser(
        description="Performance optimization benchmarking for AI agents"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Number of iterations per benchmark (default: 100)",
    )
    parser.add_argument(
        "--feature",
        choices=["mlflow", "features", "validation", "config", "all"],
        default="all",
        help="Which feature to benchmark",
    )
    parser.add_argument("--output", type=str, help="Output JSON file path")

    args = parser.parse_args()

    optimizer = PerformanceOptimizer(iterations=args.iterations)

    if args.feature == "all":
        results = optimizer.run_all_benchmarks()
    else:
        # Run specific benchmark
        benchmark_map = {
            "mlflow": optimizer.benchmark_mlflow_logging,
            "features": optimizer.benchmark_feature_retrieval,
            "validation": optimizer.benchmark_validation_overhead,
            "config": optimizer.benchmark_config_loading,
        }
        results = {
            "timestamp": datetime.now().isoformat(),
            "benchmarks": {args.feature: benchmark_map[args.feature]()},
        }

    if args.output:
        output_path = optimizer.export_json(args.output)
        print(f"Results saved to: {output_path}")
    else:
        print(json.dumps(results, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
