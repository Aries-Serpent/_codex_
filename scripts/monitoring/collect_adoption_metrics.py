#!/usr/bin/env python
"""Automated Adoption Metrics Collection for AI Agent Analysis

This script provides agent-consumable metrics about Phase 6 feature adoption.
No human intervention required - designed for autonomous monitoring and analysis.

Output Format: JSON with structured metrics for agent decision-making

Usage:
    python scripts/monitoring/collect_adoption_metrics.py --output metrics.json
    python scripts/monitoring/collect_adoption_metrics.py --days 7 --format json

Agent Integration:
    from scripts.monitoring.collect_adoption_metrics import AdoptionMetricsCollector
    collector = AdoptionMetricsCollector(days=7)
    metrics = collector.collect_all()
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# TARGET_RUN_COUNT represents full adoption baseline (100 runs = 100% adoption)
TARGET_RUN_COUNT = 100.0


class AdoptionMetricsCollector:
    """Agent-driven metrics collector for MLOps feature adoption."""

    def __init__(self, days: int = 7, base_path: Path = None):
        self.days = days
        self.base_path = base_path or Path.cwd()
        self.cutoff_time = datetime.now() - timedelta(days=days)

    def collect_mlflow_metrics(self) -> Dict[str, Any]:
        """Collect MLflow adoption metrics.

        Returns:
            Dict with structured metrics for agent analysis
        """
        metrics = {
            "feature": "mlflow_tracking",
            "enabled": False,
            "runs_total": 0,
            "runs_success": 0,
            "runs_failed": 0,
            "experiments": 0,
            "avg_duration_seconds": None,
            "adoption_score": 0.0,
        }

        try:
            import mlflow

            mlflow.set_tracking_uri("file://./mlruns")

            # Get experiments
            experiments = mlflow.search_experiments()
            metrics["experiments"] = len(experiments)
            metrics["enabled"] = True

            # Get runs from last N days
            cutoff_ms = int(self.cutoff_time.timestamp() * 1000)
            all_runs = []

            for exp in experiments:
                runs = mlflow.search_runs(
                    experiment_ids=[exp.experiment_id],
                    filter_string=f"attributes.start_time > {cutoff_ms}",
                )
                all_runs.extend(runs.to_dict("records") if not runs.empty else [])

            metrics["runs_total"] = len(all_runs)

            if all_runs:
                # Calculate success/failure
                failed = sum(1 for r in all_runs if r.get("status") == "FAILED")
                metrics["runs_success"] = metrics["runs_total"] - failed
                metrics["runs_failed"] = failed

                # Calculate average duration
                durations = [
                    (r.get("end_time", 0) - r.get("start_time", 0)) / 1000
                    for r in all_runs
                    if r.get("end_time") and r.get("start_time")
                ]
                if durations:
                    metrics["avg_duration_seconds"] = sum(durations) / len(durations)

                # Calculate adoption score (0-1)
                metrics["adoption_score"] = min(1.0, len(all_runs) / TARGET_RUN_COUNT)

        except ImportError as e:
           logger.debug(f"ImportError: {e}")
            logger.debug("MLflow not available")
        except Exception as e:
           logger.debug(f"Exception: {e}")
            logger.debug(f"MLflow metrics collection failed: {e}")

        return metrics

    def collect_feature_store_metrics(self) -> Dict[str, Any]:
        """Collect feature store metrics.

        Returns:
            Dict with feature store health and usage metrics
        """
        metrics = {
            "feature": "feature_store",
            "enabled": False,
            "feature_groups": 0,
            "healthy_groups": 0,
            "stale_groups": 0,
            "avg_age_hours": None,
            "sla_compliance": None,
            "adoption_score": 0.0,
        }

        try:
            fs_path = self.base_path / "artifacts/features/production"
            registry_path = fs_path / "registry.json"

            if not registry_path.exists():
                return metrics

            metrics["enabled"] = True

            with open(registry_path) as f:
                registry = json.load(f)

            features = registry.get("features", [])
            metrics["feature_groups"] = len(features)

            # Analyze feature health
            now = datetime.now()
            ages = []

            for feature in features:
                last_updated = feature.get("last_updated")
                if last_updated:
                    updated = datetime.fromisoformat(last_updated)
                    age_hours = (now - updated).total_seconds() / 3600
                    ages.append(age_hours)

                    # Check if stale (>48h)
                    if age_hours > 48:
                        metrics["stale_groups"] += 1
                    else:
                        metrics["healthy_groups"] += 1

            if ages:
                metrics["avg_age_hours"] = sum(ages) / len(ages)

                # SLA compliance: <2h freshness
                compliant = sum(1 for age in ages if age < 2)
                metrics["sla_compliance"] = compliant / len(ages)

            # Adoption score based on registration count
            metrics["adoption_score"] = min(1.0, len(features) / 10.0)

        except Exception as e:
           logger.debug(f"Exception: {e}")
            logger.debug(f"Feature store metrics failed: {e}")

        return metrics

    def collect_validation_metrics(self) -> Dict[str, Any]:
        """Collect data validation metrics.

        Returns:
            Dict with validation coverage and pass rates
        """
        metrics = {
            "feature": "data_validation",
            "enabled": False,
            "validations_total": 0,
            "validations_passed": 0,
            "validations_failed": 0,
            "datasets_validated": [],
            "pass_rate": None,
            "adoption_score": 0.0,
        }

        try:
            reports_dir = self.base_path / "artifacts/validation_reports"

            if not reports_dir.exists():
                return metrics

            metrics["enabled"] = True

            # Get reports from last N days
            recent_reports = []
            for report_file in reports_dir.glob("*.json"):
                try:
                    mtime = datetime.fromtimestamp(report_file.stat().st_mtime)
                    if mtime > self.cutoff_time:
                        with open(report_file) as f:
                            report = json.load(f)
                        recent_reports.append(report)
                except Exception:
                    continue

            metrics["validations_total"] = len(recent_reports)

            if recent_reports:
                passed = sum(1 for r in recent_reports if r.get("passed", False))
                metrics["validations_passed"] = passed
                metrics["validations_failed"] = len(recent_reports) - passed
                metrics["pass_rate"] = passed / len(recent_reports)

                # Get unique datasets
                datasets = set(
                    r.get("dataset_name") for r in recent_reports if r.get("dataset_name")
                )
                metrics["datasets_validated"] = sorted(list(datasets))

                # Adoption score based on validation count
                metrics["adoption_score"] = min(1.0, len(recent_reports) / 50.0)

        except Exception as e:
           logger.debug(f"Exception: {e}")
            logger.debug(f"Validation metrics failed: {e}")

        return metrics

    def collect_evaluation_metrics(self) -> Dict[str, Any]:
        """Collect evaluation runner metrics.

        Returns:
            Dict with evaluation coverage metrics
        """
        metrics = {
            "feature": "evaluation",
            "enabled": False,
            "evaluations_total": 0,
            "models_evaluated": [],
            "avg_accuracy": None,
            "adoption_score": 0.0,
        }

        try:
            eval_dir = self.base_path / "artifacts/evaluation_reports"

            if not eval_dir.exists():
                return metrics

            metrics["enabled"] = True

            # Count recent evaluations
            recent_count = 0
            accuracies = []
            models = set()

            for report_file in eval_dir.glob("*.json"):
                try:
                    mtime = datetime.fromtimestamp(report_file.stat().st_mtime)
                    if mtime > self.cutoff_time:
                        recent_count += 1
                        with open(report_file) as f:
                            report = json.load(f)

                        if "accuracy" in report:
                            accuracies.append(report["accuracy"])

                        if "model_name" in report:
                            models.add(report["model_name"])
                except Exception:
                    continue

            metrics["evaluations_total"] = recent_count
            metrics["models_evaluated"] = sorted(list(models))

            if accuracies:
                metrics["avg_accuracy"] = sum(accuracies) / len(accuracies)

            metrics["adoption_score"] = min(1.0, recent_count / 20.0)

        except Exception as e:
           logger.debug(f"Exception: {e}")
            logger.debug(f"Evaluation metrics failed: {e}")

        return metrics

    def collect_training_enhancements_metrics(self) -> Dict[str, Any]:
        """Collect training enhancements usage metrics.

        Returns:
            Dict with early stopping and scheduler usage
        """
        metrics = {
            "feature": "training_enhancements",
            "early_stopping_enabled": False,
            "scheduler_enabled": False,
            "checkpointing_enabled": False,
            "adoption_score": 0.0,
        }

        try:
            config_path = self.base_path / "configs/production/training.yaml"

            if config_path.exists():
                import yaml

                with open(config_path) as f:
                    config = yaml.safe_load(f)

                training = config.get("training_enhancements", {})

                early_stopping = training.get("early_stopping", {})
                metrics["early_stopping_enabled"] = early_stopping.get("enabled", False)

                scheduler = training.get("scheduler", {})
                metrics["scheduler_enabled"] = scheduler.get("type") is not None

                checkpointing = training.get("checkpointing", {})
                metrics["checkpointing_enabled"] = checkpointing.get("enabled", False)

                # Adoption score: count of enabled features
                enabled_count = sum(
                    [
                        metrics["early_stopping_enabled"],
                        metrics["scheduler_enabled"],
                        metrics["checkpointing_enabled"],
                    ]
                )
                metrics["adoption_score"] = enabled_count / 3.0

        except Exception as e:
           logger.debug(f"Exception: {e}")
            logger.debug(f"Training enhancements metrics failed: {e}")

        return metrics

    def collect_all(self) -> Dict[str, Any]:
        """Collect all adoption metrics.

        Returns:
            Complete metrics report for agent analysis
        """
        logger.info(f"Collecting adoption metrics (last {self.days} days)")

        report = {
            "timestamp": datetime.now().isoformat(),
            "collection_period_days": self.days,
            "metrics": {
                "mlflow": self.collect_mlflow_metrics(),
                "feature_store": self.collect_feature_store_metrics(),
                "validation": self.collect_validation_metrics(),
                "evaluation": self.collect_evaluation_metrics(),
                "training": self.collect_training_enhancements_metrics(),
            },
        }

        # Calculate overall adoption score
        scores = [m["adoption_score"] for m in report["metrics"].values()]
        report["overall_adoption_score"] = sum(scores) / len(scores) if scores else 0.0

        # Generate analysis summary
        enabled_features = sum(1 for m in report["metrics"].values() if m.get("enabled", False))
        report["summary"] = {
            "enabled_features": enabled_features,
            "total_features": len(report["metrics"]),
            "adoption_percentage": (enabled_features / len(report["metrics"])) * 100,
            "overall_score": report["overall_adoption_score"],
        }

        # Add recommendations for agents
        report["agent_recommendations"] = self._generate_recommendations(report)

        return report

    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations for agents.

        Args:
            report: Complete metrics report

        Returns:
            List of actionable recommendations
        """
        recommendations = []

        metrics = report["metrics"]

        # MLflow recommendations
        if metrics["mlflow"]["enabled"] and metrics["mlflow"]["runs_total"] < 10:
            recommendations.append(
                "RECOMMENDATION: MLflow enabled but low usage. Consider increasing experiment logging."
            )

        # Feature store recommendations
        if metrics["feature_store"]["enabled"]:
            if metrics["feature_store"]["stale_groups"] > 0:
                recommendations.append(
                    f"ACTION_REQUIRED: {metrics['feature_store']['stale_groups']} feature groups are stale (>48h). Trigger feature refresh."
                )

            if (
                metrics["feature_store"]["sla_compliance"]
                and metrics["feature_store"]["sla_compliance"] < 0.95
            ):
                recommendations.append(
                    "WARNING: Feature freshness SLA below 95%. Review feature update pipeline."
                )

        # Validation recommendations
        if metrics["validation"]["enabled"]:
            if metrics["validation"]["pass_rate"] and metrics["validation"]["pass_rate"] < 0.95:
                recommendations.append(
                    f"ALERT: Validation pass rate at {metrics['validation']['pass_rate']:.1%}. Investigate data quality issues."
                )

        # Overall adoption
        if report["overall_adoption_score"] < 0.5:
            recommendations.append(
                "LOW_ADOPTION: Overall adoption score below 50%. Consider enabling more features."
            )

        if not recommendations:
            recommendations.append("STATUS: All systems operating within normal parameters.")

        return recommendations

    def export_json(self, output_path: str = None) -> str:
        """Export metrics to JSON file.

        Args:
            output_path: Output file path (optional)

        Returns:
            Path to exported file
        """
        metrics = self.collect_all()

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"adoption_metrics_{timestamp}.json"

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(metrics, f, indent=2)

        logger.info(f"Metrics exported to: {output_file}")
        return str(output_file)


def main():
    """CLI entry point for agent execution."""
    parser = argparse.ArgumentParser(
        description="Collect MLOps adoption metrics for AI agent analysis"
    )
    parser.add_argument(
        "--days", type=int, default=7, help="Number of days to analyze (default: 7)"
    )
    parser.add_argument("--output", type=str, help="Output JSON file path")
    parser.add_argument(
        "--format", choices=["json", "compact"], default="json", help="Output format"
    )

    args = parser.parse_args()

    collector = AdoptionMetricsCollector(days=args.days)
    metrics = collector.collect_all()

    if args.output:
        output_path = collector.export_json(args.output)
        print(f"Metrics saved to: {output_path}")
    else:
        # Print to stdout for agent consumption
        if args.format == "compact":
            print(json.dumps(metrics))
        else:
            print(json.dumps(metrics, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
