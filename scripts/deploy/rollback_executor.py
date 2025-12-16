#!/usr/bin/env python
"""Automated Rollback Executor for AI Agents

Executes rollback procedures for Phase 6 features with zero human intervention.
Designed for agent-driven recovery from deployment issues.

Usage:
    python scripts/deploy/rollback_executor.py --feature mlflow
    python scripts/deploy/rollback_executor.py --all --dry-run

Agent Integration:
    from scripts.deploy.rollback_executor import RollbackExecutor
    executor = RollbackExecutor()
    result = executor.rollback_feature("mlflow")
"""

import argparse
import json
import logging
import sys
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class RollbackExecutor:
    """Agent-driven rollback executor for MLOps features."""

    def __init__(self, base_path: Path = None, dry_run: bool = False):
        self.base_path = base_path or Path.cwd()
        self.dry_run = dry_run
        self.rollback_log = []

    def _log_action(self, action: str, status: str, details: str = ""):
        """Log rollback action for audit trail."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "details": details,
            "dry_run": self.dry_run,
        }
        self.rollback_log.append(entry)
        logger.info(f"{action}: {status} - {details}")

    def rollback_mlflow(self) -> Dict[str, Any]:
        """Rollback MLflow tracking feature.

        Returns:
            Rollback execution report
        """
        logger.info("Rolling back MLflow tracking feature")

        try:
            config_path = self.base_path / "configs/production/tracking.yaml"

            if not config_path.exists():
                return {"feature": "mlflow", "status": "skipped", "reason": "Config file not found"}

            # Backup current config
            backup_path = config_path.with_suffix(".yaml.backup")

            if not self.dry_run:
                shutil.copy(config_path, backup_path)
                self._log_action("backup_config", "success", str(backup_path))

                # Disable MLflow in config
                with open(config_path) as f:
                    config = yaml.safe_load(f)

                if "tracking" in config and "mlflow" in config["tracking"]:
                    config["tracking"]["mlflow"]["enabled"] = False

                    with open(config_path, "w") as f:
                        yaml.dump(config, f, default_flow_style=False)

                    self._log_action("disable_mlflow", "success", "Set enabled=false")
            else:
                self._log_action("disable_mlflow", "dry_run", "Would set enabled=false")

            return {
                "feature": "mlflow",
                "status": "success",
                "actions": ["Backed up configuration", "Disabled MLflow tracking"],
                "backup_path": str(backup_path) if not self.dry_run else None,
            }

        except Exception as e:
            self._log_action("rollback_mlflow", "error", str(e))
            return {"feature": "mlflow", "status": "error", "error": str(e)}

    def rollback_feature_store(self) -> Dict[str, Any]:
        """Rollback feature store.

        Returns:
            Rollback execution report
        """
        logger.info("Rolling back feature store")

        try:
            config_path = self.base_path / "configs/production/features.yaml"
            artifacts_path = self.base_path / "artifacts/features"

            actions = []

            # Disable in config
            if config_path.exists():
                if not self.dry_run:
                    with open(config_path) as f:
                        config = yaml.safe_load(f)

                    if "feature_store" in config:
                        config["feature_store"]["enabled"] = False

                        with open(config_path, "w") as f:
                            yaml.dump(config, f, default_flow_style=False)

                        self._log_action("disable_feature_store", "success", "Set enabled=false")
                        actions.append("Disabled feature store in config")
                else:
                    self._log_action("disable_feature_store", "dry_run", "Would set enabled=false")
                    actions.append("[DRY RUN] Would disable feature store")

            # Archive artifacts (don't delete, for safety)
            if artifacts_path.exists():
                archive_path = (
                    artifacts_path.parent
                    / f"features_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )

                if not self.dry_run:
                    shutil.move(str(artifacts_path), str(archive_path))
                    self._log_action("archive_artifacts", "success", str(archive_path))
                    actions.append(f"Archived artifacts to {archive_path}")
                else:
                    self._log_action("archive_artifacts", "dry_run", "Would archive artifacts")
                    actions.append("[DRY RUN] Would archive artifacts")

            return {"feature": "feature_store", "status": "success", "actions": actions}

        except Exception as e:
            self._log_action("rollback_feature_store", "error", str(e))
            return {"feature": "feature_store", "status": "error", "error": str(e)}

    def rollback_validation(self) -> Dict[str, Any]:
        """Rollback data validation.

        Returns:
            Rollback execution report
        """
        logger.info("Rolling back data validation")

        try:
            config_path = self.base_path / "configs/production/data_validation.yaml"

            if not config_path.exists():
                return {
                    "feature": "data_validation",
                    "status": "skipped",
                    "reason": "Config not found",
                }

            if not self.dry_run:
                with open(config_path) as f:
                    config = yaml.safe_load(f)

                if "data_validation" in config:
                    config["data_validation"]["enabled"] = False

                    with open(config_path, "w") as f:
                        yaml.dump(config, f, default_flow_style=False)

                    self._log_action("disable_validation", "success", "Set enabled=false")
            else:
                self._log_action("disable_validation", "dry_run", "Would set enabled=false")

            return {
                "feature": "data_validation",
                "status": "success",
                "actions": ["Disabled data validation"],
            }

        except Exception as e:
            self._log_action("rollback_validation", "error", str(e))
            return {"feature": "data_validation", "status": "error", "error": str(e)}

    def rollback_all(self) -> Dict[str, Any]:
        """Rollback all Phase 6 features.

        Returns:
            Complete rollback report
        """
        logger.info("Rolling back all Phase 6 features")

        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "rollbacks": {
                "mlflow": self.rollback_mlflow(),
                "feature_store": self.rollback_feature_store(),
                "data_validation": self.rollback_validation(),
            },
        }

        # Summary
        successful = sum(1 for r in report["rollbacks"].values() if r["status"] == "success")
        total = len(report["rollbacks"])

        report["summary"] = {
            "total_features": total,
            "successful_rollbacks": successful,
            "failed_rollbacks": total - successful,
            "all_successful": successful == total,
        }

        report["audit_log"] = self.rollback_log

        return report

    def export_report(self, output_path: str = None) -> str:
        """Export rollback report to JSON.

        Args:
            output_path: Output file path (optional)

        Returns:
            Path to exported file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"rollback_report_{timestamp}.json"

        report = self.rollback_all()

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Rollback report exported to: {output_file}")
        return str(output_file)


def main():
    """CLI entry point for agent execution."""
    parser = argparse.ArgumentParser(description="Automated rollback executor for AI agents")
    parser.add_argument(
        "--feature",
        choices=["mlflow", "feature_store", "validation", "all"],
        default="all",
        help="Which feature to rollback",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulate rollback without making changes"
    )
    parser.add_argument("--output", type=str, help="Output report file path")

    args = parser.parse_args()

    executor = RollbackExecutor(dry_run=args.dry_run)

    if args.feature == "all":
        report = executor.rollback_all()
    else:
        # Rollback specific feature
        rollback_map = {
            "mlflow": executor.rollback_mlflow,
            "feature_store": executor.rollback_feature_store,
            "validation": executor.rollback_validation,
        }
        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": args.dry_run,
            "rollback": rollback_map[args.feature](),
            "audit_log": executor.rollback_log,
        }

    if args.output:
        output_path = executor.export_report(args.output)
        print(f"Report saved to: {output_path}")
    else:
        print(json.dumps(report, indent=2))

    # Exit with error code if any rollbacks failed
    if report.get("summary", {}).get("all_successful", True):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
