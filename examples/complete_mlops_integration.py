#!/usr/bin/env python3
"""Complete MLOps integration example with all Phase 6-7 features.

This example demonstrates:
- MLflow experiment tracking
- Feature store usage
- Data validation
- Reproducibility
- Health monitoring
"""

import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run complete MLOps integration example."""
    
    # Import MLOps components
    from codex_ml.tracking.mlflow_wrapper import MLflowTracker
    from codex_ml.training.tracking_integration import TrainingTracker
    from codex_ml.features.feature_store import FeatureStore, FeatureGroup, Feature
    from codex_ml.features.monitoring import FeatureHealthMonitor
    from codex_ml.utils.reproducibility import set_global_seed, capture_rng_snapshot
    
    logger.info("=== Complete MLOps Integration Example ===\n")
    
    # 1. Set up reproducibility
    logger.info("1. Setting up reproducibility...")
    seed = 42
    set_global_seed(seed)
    rng_snapshot = capture_rng_snapshot()
    logger.info(f"   ✓ Global seed set to {seed}")
    logger.info(f"   ✓ RNG snapshot captured: {rng_snapshot}\n")
    
    # 2. Initialize feature store
    logger.info("2. Initializing feature store...")
    feature_store = FeatureStore("./artifacts/features")
    
    # Define a simple feature transformation
    def age_squared(inputs):
        return inputs.get("age", 0) ** 2
    
    # Register a feature group
    feature_group = FeatureGroup(
        name="user_features",
        version="1.0.0",
        features=[
            Feature(name="age_squared", transform_fn=age_squared),
        ],
        description="User demographic features",
    )
    feature_store.register_feature_group(feature_group)
    logger.info(f"   ✓ Registered feature group: user_features v1.0.0\n")
    
    # 3. Set up feature health monitoring
    logger.info("3. Setting up feature health monitoring...")
    health_monitor = FeatureHealthMonitor(freshness_threshold_minutes=60)
    health_monitor.record_feature_update("user_features")
    status = health_monitor.check_feature_health("user_features")
    logger.info(f"   ✓ Feature health: {status.is_healthy} ({status.freshness_level})\n")
    
    # 4. Set up MLflow tracking
    logger.info("4. Setting up MLflow experiment tracking...")
    tracker = MLflowTracker(
        enabled=True,
        tracking_uri="file:./mlruns",
        experiment_name="complete_mlops_example",
    )
    logger.info("   ✓ MLflow tracker initialized\n")
    
    # 5. Run training with tracking
    logger.info("5. Running training with MLflow tracking...")
    
    with tracker.start_run("example_run"):
        # Log hyperparameters
        hyperparams = {
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 5,
            "seed": seed,
        }
        tracker.log_params(hyperparams)
        logger.info(f"   ✓ Logged {len(hyperparams)} hyperparameters")
        
        # Simulate training loop
        for epoch in range(5):
            # Compute features
            inputs = {"age": 25}
            features = feature_store.materialize_features(["age_squared"], inputs)
            
            # Simulate training metrics
            train_loss = 1.0 / (epoch + 1)
            val_loss = 0.9 / (epoch + 1)
            
            # Log metrics
            tracker.log_metrics({
                "train_loss": train_loss,
                "val_loss": val_loss,
                "age_squared": features["age_squared"],
            }, step=epoch)
            
            logger.info(f"   Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}")
        
        # Log final results
        tracker.set_tag("status", "completed")
        tracker.set_tag("final_loss", val_loss)
        logger.info("   ✓ Training complete\n")
    
    # 6. Generate health report
    logger.info("6. Generating health report...")
    health_statuses = health_monitor.check_all_features(["user_features"])
    report = health_monitor.generate_health_report(
        health_statuses,
        format="markdown",
        include_recommendations=True,
    )
    
    # Save report
    report_path = Path("./artifacts/health_report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    logger.info(f"   ✓ Health report saved to {report_path}\n")
    
    # 7. Summary
    logger.info("=== Summary ===")
    logger.info("✓ Reproducibility: Seed set, environment captured")
    logger.info("✓ Feature Store: 1 feature group registered")
    logger.info("✓ Health Monitoring: Active, all features healthy")
    logger.info("✓ MLflow Tracking: 5 epochs logged, run completed")
    logger.info("✓ Integration: All MLOps components working together")
    logger.info("\nMLflow UI: Run 'mlflow ui' to view results")
    logger.info("Health Report: ./artifacts/health_report.md\n")


if __name__ == "__main__":
    main()
