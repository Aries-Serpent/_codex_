#!/usr/bin/env python
"""Track Phase 6 MLOps Feature Adoption Metrics"""
import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

try:
    import yaml
except ImportError:
    yaml = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Scoring weights for adoption score calculation (decimal values where 0.10 = 10%)
SCORING_WEIGHTS = {
    "mlflow_config": 0.10,
    "mlflow_experiments": 0.05,
    "mlflow_runs": 0.05,
    "mlflow_artifacts": 0.05,
    "feature_store_config": 0.10,
    "feature_store_defined": 0.075,
    "feature_store_registered": 0.075,
    "validation_config": 0.20,
    "evaluation_config": 0.15,
    "monitoring_config": 0.15,
}

# Individual constants for easier access
MLFLOW_CONFIG_WEIGHT = SCORING_WEIGHTS["mlflow_config"]
MLFLOW_EXPERIMENTS_WEIGHT = SCORING_WEIGHTS["mlflow_experiments"]
MLFLOW_RUNS_WEIGHT = SCORING_WEIGHTS["mlflow_runs"]
MLFLOW_ARTIFACTS_WEIGHT = SCORING_WEIGHTS["mlflow_artifacts"]
FEATURE_STORE_CONFIG_WEIGHT = SCORING_WEIGHTS["feature_store_config"]
FEATURE_STORE_DEFINED_WEIGHT = SCORING_WEIGHTS["feature_store_defined"]
FEATURE_STORE_REGISTERED_WEIGHT = SCORING_WEIGHTS["feature_store_registered"]
VALIDATION_CONFIG_WEIGHT = SCORING_WEIGHTS["validation_config"]
EVALUATION_CONFIG_WEIGHT = SCORING_WEIGHTS["evaluation_config"]
MONITORING_CONFIG_WEIGHT = SCORING_WEIGHTS["monitoring_config"]

def _validate_scoring_weights() -> None:
    """
    Validate that scoring weights sum to 1.0.
    
    Raises:
        ValueError: If weights don't sum to approximately 1.0
    """
    # WEIGHT_SUM_EPSILON is the tolerance for floating-point weight sum validation
    WEIGHT_SUM_EPSILON = 0.001
    total_weight = sum(SCORING_WEIGHTS.values())
    if abs(total_weight - 1.0) >= WEIGHT_SUM_EPSILON:
        raise ValueError(
            f"Scoring weights must sum to 1.0, got {total_weight}. "
            f"Please check SCORING_WEIGHTS configuration."
        )

class AdoptionTracker:
    """
    Tracks adoption metrics for Phase 6 MLOps features.
    
    Collects metrics across:
    - MLflow tracking usage
    - Feature store utilization
    - Data validation adoption
    - Evaluation standardization
    - Monitoring and training enhancements
    """
    
    def __init__(self, days: int = 7):
        _validate_scoring_weights()  # Validate weights on initialization
        self.days = days
        self.metrics = {
            "timestamp": datetime.now().isoformat(),
            "period_days": days,
            "mlflow": {},
            "feature_store": {},
            "validation": {},
            "evaluation": {},
            "monitoring": {},
        }
    
    def _collect_mlflow_metrics(self) -> Dict[str, Any]:
        """Collect MLflow tracking adoption metrics."""
        mlflow_metrics = {
            "experiments_created": 0,
            "runs_logged": 0,
            "artifacts_stored": 0,
            "enabled_in_configs": False,
        }
        
        # Check if MLflow is configured in production configs
        mlflow_config = Path("configs/production/tracking.yaml")
        if mlflow_config.exists():
            mlflow_metrics["enabled_in_configs"] = True
            logger.info("✓ MLflow tracking configuration found")
        
        # Check for MLflow artifacts directory
        mlflow_dir = Path("mlruns")
        if mlflow_dir.exists():
            try:
                # Count experiment directories
                experiments = [d for d in mlflow_dir.iterdir() if d.is_dir()]
                mlflow_metrics["experiments_created"] = len(experiments)
                
                # Count run directories across experiments
                run_count = 0
                artifact_count = 0
                for exp_dir in experiments:
                    runs = [d for d in exp_dir.iterdir() if d.is_dir()]
                    run_count += len(runs)
                    for run_dir in runs:
                        artifacts_dir = run_dir / "artifacts"
                        if artifacts_dir.exists():
                            # Count files efficiently using os.walk (more performant than rglob)
                            # MAX_ARTIFACTS_PER_RUN is a performance safeguard to prevent excessive file system traversal
                            MAX_ARTIFACTS_PER_RUN = 10000
                            try:
                                file_count = 0
                                for root, dirs, files in os.walk(artifacts_dir):
                                    file_count += len(files)
                                    if file_count >= MAX_ARTIFACTS_PER_RUN:
                                        file_count = MAX_ARTIFACTS_PER_RUN
                                        dirs.clear()  # Prevent os.walk from descending further
                                        break
                                artifact_count += file_count
                            except Exception:
                                # If there's an error reading artifacts, skip counting for this run
                                pass
                
                mlflow_metrics["runs_logged"] = run_count
                mlflow_metrics["artifacts_stored"] = artifact_count
                logger.info(f"✓ MLflow: {mlflow_metrics['experiments_created']} experiments, "
                          f"{mlflow_metrics['runs_logged']} runs, "
                          f"{mlflow_metrics['artifacts_stored']} artifacts")
            except Exception as e:
                logger.warning(f"Error collecting MLflow metrics: {e}")
        
        return mlflow_metrics
    
    def _collect_feature_store_metrics(self) -> Dict[str, Any]:
        """Collect feature store adoption metrics."""
        fs_metrics = {
            "feature_groups_defined": 0,
            "feature_groups_registered": 0,
            "enabled_in_configs": False,
        }
        
        # Check if feature store is configured
        fs_config = Path("configs/production/features.yaml")
        if fs_config.exists():
            fs_metrics["enabled_in_configs"] = True
            if yaml is not None:
                try:
                    with open(fs_config) as f:
                        config = yaml.safe_load(f)
                        if config and "feature_store" in config:
                            feature_groups = config["feature_store"].get("feature_groups", [])
                            fs_metrics["feature_groups_defined"] = len(feature_groups)
                    logger.info(f"✓ Feature Store: {fs_metrics['feature_groups_defined']} groups defined")
                except Exception as e:
                    logger.warning(f"Error reading feature store config: {e}")
            else:
                logger.warning("YAML library not available, skipping feature group count")
        
        # Check for registered feature groups
        fs_storage = Path("data/feature_store")
        if fs_storage.exists():
            try:
                registered = len([d for d in fs_storage.iterdir() if d.is_dir()])
                fs_metrics["feature_groups_registered"] = registered
                logger.info(f"✓ Feature Store: {registered} groups registered")
            except Exception as e:
                logger.warning(f"Error checking feature store storage: {e}")
        
        return fs_metrics
    
    def _collect_validation_metrics(self) -> Dict[str, Any]:
        """Collect data validation adoption metrics."""
        validation_metrics = {
            "enabled_in_configs": False,
            "validation_runs": 0,
        }
        
        # Check if validation is configured
        validation_config = Path("configs/production/validation.yaml")
        if validation_config.exists():
            validation_metrics["enabled_in_configs"] = True
            logger.info("✓ Data validation configuration found")
        
        return validation_metrics
    
    def _collect_evaluation_metrics(self) -> Dict[str, Any]:
        """Collect evaluation standardization metrics."""
        eval_metrics = {
            "enabled_in_configs": False,
        }
        
        # Check if evaluation is configured
        eval_config = Path("configs/production/evaluation.yaml")
        if eval_config.exists():
            eval_metrics["enabled_in_configs"] = True
            logger.info("✓ Evaluation configuration found")
        
        return eval_metrics
    
    def _collect_monitoring_metrics(self) -> Dict[str, Any]:
        """Collect monitoring and training enhancement metrics."""
        monitoring_metrics = {
            "enabled_in_configs": False,
        }
        
        # Check if monitoring is configured
        monitoring_config = Path("configs/production/monitoring.yaml")
        if monitoring_config.exists():
            monitoring_metrics["enabled_in_configs"] = True
            logger.info("✓ Monitoring configuration found")
        
        return monitoring_metrics
    
    def _calculate_adoption_score(self) -> float:
        """
        Calculate overall adoption score (0.0 to 1.0).
        
        Scoring weights (decimal values where 0.10 = 10%):
        - MLflow tracking: 0.25 total (config 0.10 + experiments 0.05 + runs 0.05 + artifacts 0.05)
        - Feature store: 0.25 total (config 0.10 + defined 0.075 + registered 0.075)
        - Data validation: 0.20 total (config 0.20)
        - Evaluation: 0.15 total (config 0.15)
        - Monitoring: 0.15 total (config 0.15)
        
        Total: 1.00 (100%)
        """
        score = 0.0
        
        # MLflow (25 points total)
        if self.metrics["mlflow"].get("enabled_in_configs"):
            score += MLFLOW_CONFIG_WEIGHT
        if self.metrics["mlflow"].get("experiments_created", 0) > 0:
            score += MLFLOW_EXPERIMENTS_WEIGHT
        if self.metrics["mlflow"].get("runs_logged", 0) > 0:
            score += MLFLOW_RUNS_WEIGHT
        if self.metrics["mlflow"].get("artifacts_stored", 0) > 0:
            score += MLFLOW_ARTIFACTS_WEIGHT
        
        # Feature Store (25 points total)
        if self.metrics["feature_store"].get("enabled_in_configs"):
            score += FEATURE_STORE_CONFIG_WEIGHT
        if self.metrics["feature_store"].get("feature_groups_defined", 0) > 0:
            score += FEATURE_STORE_DEFINED_WEIGHT
        if self.metrics["feature_store"].get("feature_groups_registered", 0) > 0:
            score += FEATURE_STORE_REGISTERED_WEIGHT
        
        # Validation (20 points total)
        if self.metrics["validation"].get("enabled_in_configs"):
            score += VALIDATION_CONFIG_WEIGHT
        
        # Evaluation (15 points total)
        if self.metrics["evaluation"].get("enabled_in_configs"):
            score += EVALUATION_CONFIG_WEIGHT
        
        # Monitoring (15 points total)
        if self.metrics["monitoring"].get("enabled_in_configs"):
            score += MONITORING_CONFIG_WEIGHT
        
        return round(score, 2)
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all Phase 6 adoption metrics."""
        logger.info("Collecting Phase 6 adoption metrics...")
        
        # Collect metrics from each area
        self.metrics["mlflow"] = self._collect_mlflow_metrics()
        self.metrics["feature_store"] = self._collect_feature_store_metrics()
        self.metrics["validation"] = self._collect_validation_metrics()
        self.metrics["evaluation"] = self._collect_evaluation_metrics()
        self.metrics["monitoring"] = self._collect_monitoring_metrics()
        
        # Calculate overall adoption score
        self.metrics["overall_adoption_score"] = self._calculate_adoption_score()
        
        logger.info(f"✓ Overall adoption score: {self.metrics['overall_adoption_score']:.0%}")
        
        return self.metrics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    
    tracker = AdoptionTracker(days=args.days)
    metrics = tracker.collect_all_metrics()
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(metrics, f, indent=2)
    else:
        print(json.dumps(metrics, indent=2))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
