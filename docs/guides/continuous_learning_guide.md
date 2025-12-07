# Continuous Learning Guide

## Overview

The Continuous Learning Pipeline enables automatic model retraining when drift is detected, maintaining model performance without manual intervention.

## Quick Start

```python
from codex_ml.training.continuous_learning import ContinuousLearningPipeline
from codex_ml.monitoring.drift_detection import ComprehensiveDriftMonitor

# Initialize pipeline
pipeline = ContinuousLearningPipeline(
    model_name="my_model",
    drift_threshold=0.15,
    min_samples_retrain=1000
)

# Initialize drift monitor
monitor = ComprehensiveDriftMonitor(
    data_threshold=0.1,
    model_threshold=0.1
)
```

## Core Concepts

### 1. Model Registry

Track all model versions with metadata:

```python
from codex_ml.training.continuous_learning import ModelRegistry

registry = ModelRegistry("models/registry.json")

# Get latest model
latest = registry.get_latest()
print(f"Latest version: {latest.version}")
print(f"Metrics: {latest.metrics}")

# Get specific version
v1 = registry.get_by_version("v1.0")
```

### 2. Drift Monitoring

Monitor for data, config, and model drift:

```python
from codex_ml.monitoring.drift_detection import ComprehensiveDriftMonitor

monitor = ComprehensiveDriftMonitor(
    data_threshold=0.1,
    config_threshold=0.0,
    model_threshold=0.1
)

# Monitor all drift types
results = monitor.monitor_all(
    current_data_stats={"mean": 0.5, "std": 0.2},
    baseline_data_stats={"mean": 0.48, "std": 0.19},
    current_metrics={"accuracy": 0.92, "f1": 0.89},
    baseline_metrics={"accuracy": 0.95, "f1": 0.93}
)

# Check for critical drift
if monitor.has_critical_drift():
    print("⚠️ Critical drift detected!")
    summary = monitor.get_drift_summary()
    print(f"Critical alerts: {summary['critical_count']}")
```

### 3. Auto-Retraining

Automatically retrain when drift exceeds thresholds:

```python
# Check if retraining needed
if pipeline.should_retrain(
    drift_score=0.2,
    samples_count=1500,
    current_performance={"accuracy": 0.90}
):
    print("Retraining triggered")
    
    # Execute retraining
    new_version = pipeline.retrain(
        train_fn=train_model,
        train_data=new_data,
        dataset_hash="abc123...",
        drift_score=0.2
    )
    
    print(f"New version: {new_version.version}")
    print(f"Metrics: {new_version.metrics}")
```

### 4. Model Comparison

Compare new model with production:

```python
# Compare with baseline
comparison = pipeline.compare_models(
    new_version=new_version,
    baseline_version=None,  # Uses latest from registry
    primary_metric="accuracy"
)

if comparison["is_better"]:
    print(f"✅ New model improved by {comparison['improvement']:.3f}")
    pipeline.deploy_model(new_version)
else:
    print(f"❌ New model worse by {-comparison['improvement']:.3f}")
    pipeline.rollback()
```

## Complete Workflow

### Step 1: Setup

```python
from codex_ml.training.continuous_learning import ContinuousLearningPipeline
from codex_ml.monitoring.drift_detection import ComprehensiveDriftMonitor
from codex_ml.utils.repro import DatasetManifest

# Initialize components
pipeline = ContinuousLearningPipeline(
    model_name="production_model",
    drift_threshold=0.15,
    min_samples_retrain=1000,
    performance_degradation_threshold=0.05
)

monitor = ComprehensiveDriftMonitor(
    data_threshold=0.1,
    model_threshold=0.1
)
```

### Step 2: Continuous Monitoring

```python
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger("continuous_learning")

def continuous_learning_loop():
    """Run continuous learning loop with error handling and logging."""
    
    while True:
        try:
            # 1. Collect new data
            new_data = collect_production_data()
            
            # 2. Compute statistics
            current_stats = compute_statistics(new_data)
            baseline_stats = load_baseline_statistics()
            
            # 3. Monitor for drift
            results = monitor.monitor_all(
                current_data_stats=current_stats,
                baseline_data_stats=baseline_stats,
                current_metrics=get_production_metrics(),
                baseline_metrics=load_baseline_metrics()
            )
            
            # 4. Check if retraining needed
            if monitor.has_critical_drift():
                drift_score = results["data_drift"]["score"]
                
                if pipeline.should_retrain(
                    drift_score=drift_score,
                    samples_count=len(new_data)
                ):
                    # 5. Trigger retraining
                    logger.info("Triggering retraining due to drift (score: %s)", drift_score)
                    retrain_and_deploy(new_data, drift_score)
            
            # Wait before next check (e.g., hourly)
            time.sleep(3600)
        except Exception as e:
            logger.error("Exception in continuous learning loop: %s", e, exc_info=True)
            # Optionally, wait before retrying to avoid rapid failure loops
            time.sleep(60)
```

### Step 3: Retraining Function

```python
def retrain_and_deploy(new_data, drift_score):
    """Retrain and deploy new model."""
    
    # 1. Validate dataset
    manifest = DatasetManifest("data/production")
    manifest.generate().save("data/manifest.json")
    
    # 2. Prepare training data
    train_data, eval_data = prepare_data(new_data)
    
    # 3. Define training function
    def train_fn(data):
        model = YourModel()
        trainer = YourTrainer(model)
        metrics = trainer.train(data)
        return model, metrics
    
    # 4. Retrain
    new_version = pipeline.retrain(
        train_fn=train_fn,
        train_data=train_data,
        dataset_hash=manifest.compute_hash(),
        drift_score=drift_score
    )
    
    # 5. Validate on eval set
    eval_metrics = evaluate_model(new_version, eval_data)
    
    # 6. Compare with production
    comparison = pipeline.compare_models(
        new_version,
        primary_metric="accuracy"
    )
    
    # 7. Deploy if better
    if comparison["is_better"]:
        print(f"✅ Deploying {new_version.version}")
        pipeline.deploy_model(new_version)
        
        # Update baseline statistics
        update_baseline_statistics(eval_metrics)
    else:
        print(f"❌ New model not better, keeping current")
```

## Configuration

### Pipeline Configuration

```python
pipeline = ContinuousLearningPipeline(
    model_name="my_model",
    
    # Retraining triggers
    drift_threshold=0.15,          # Trigger when drift > 15%
    min_samples_retrain=1000,      # Minimum samples needed
    performance_degradation_threshold=0.05,  # Max acceptable drop
    
    # Registry
    registry_path="models/registry.json"
)
```

### Monitor Configuration

```python
monitor = ComprehensiveDriftMonitor(
    data_threshold=0.1,      # Data drift threshold
    config_threshold=0.0,    # Config drift (strict)
    model_threshold=0.1      # Model performance drift
)
```

## Best Practices

### 1. Gradual Rollout

Always use gradual rollout for safety:

```python
if comparison["is_better"]:
    # Deploy to 10% of traffic first
    deploy_to_percentage(new_version, percentage=10)
    
    # Monitor for 24 hours
    time.sleep(86400)
    
    # Check performance
    if production_metrics_stable():
        # Increase to 50%
        deploy_to_percentage(new_version, percentage=50)
        time.sleep(86400)
        
        # Full rollout
        if production_metrics_stable():
            pipeline.deploy_model(new_version)
```

### 2. Automated Rollback

Implement automatic rollback on degradation:

```python
def monitor_production():
    """Monitor production performance."""
    
    current_metrics = get_production_metrics()
    baseline_metrics = load_baseline_metrics()
    
    for metric, value in current_metrics.items():
        baseline = baseline_metrics.get(metric, 0)
        
        # Check for significant degradation
        if value < baseline * 0.95:  # 5% degradation
            print(f"⚠️ Performance degraded: {metric}")
            pipeline.rollback()
            break
```

### 3. Data Validation

Always validate data before retraining:

```python
from codex_ml.utils.repro import DatasetManifest

def validate_training_data(data_path):
    """Validate data integrity."""
    
    manifest = DatasetManifest(data_path)
    
    # Check for drift
    if manifest.has_drift("baseline_manifest.json"):
        diff = manifest.verify("baseline_manifest.json")
        print(f"⚠️ Dataset drift: {len(diff['modified'])} modified files")
        
        # Decide whether to proceed
        if len(diff['modified']) > 10:
            raise ValueError("Too many files modified")
    
    return True
```

### 4. Experiment Tracking

Log all retraining experiments:

```python
from codex_ml.utils.wandb_logger import init_wandb

def retrain_with_logging(train_data, drift_score):
    """Retrain with experiment tracking."""
    
    logger = init_wandb(
        project="continuous-learning",
        name=f"retrain-{datetime.now().isoformat()}"
    )
    
    # Log configuration
    logger.log({
        "drift_score": drift_score,
        "samples_count": len(train_data),
        "trigger": "drift_threshold_exceeded"
    })
    
    # Retrain
    new_version = pipeline.retrain(...)
    
    # Log results
    logger.log({
        "new_version": new_version.version,
        "metrics": new_version.metrics,
        "improvement": comparison["improvement"]
    })
    
    logger.finish()
```

## Monitoring & Alerts

### 1. Setup Alerts

```python
def setup_drift_alerts():
    """Configure drift alerts."""
    
    alerts = {
        "critical": lambda: send_alert("Critical drift detected!"),
        "high": lambda: send_notification("High drift warning"),
        "medium": lambda: log_warning("Medium drift detected")
    }
    
    return alerts
```

### 2. Alert on Drift

```python
def monitor_with_alerts(monitor, alerts):
    """Monitor and send alerts."""
    
    results = monitor.monitor_all(...)
    
    if monitor.has_critical_drift():
        alerts["critical"]()
        
        # Save alert details
        monitor.save_alerts("alerts/drift_critical.json")
```

### 3. Metrics Dashboard

Integrate with Prometheus:

```python
from codex_ml.monitoring.metrics import MetricsCollector

metrics = MetricsCollector()

# Record drift metrics
metrics.record_gauge("drift_score", drift_score)
metrics.record_gauge("model_accuracy", accuracy)
metrics.record_gauge("retraining_triggered", 1 if triggered else 0)
```

## Troubleshooting

### Issue: Frequent Retraining

**Problem:** Model retrains too frequently

**Solution:**
```python
# Increase thresholds
pipeline = ContinuousLearningPipeline(
    drift_threshold=0.20,  # Higher threshold
    min_samples_retrain=2000  # More samples required
)

# Add cooldown period
last_retrain_time = None

def should_retrain_with_cooldown(cooldown_hours=24):
    if last_retrain_time:
        elapsed = (datetime.now() - last_retrain_time).total_seconds() / 3600
        if elapsed < cooldown_hours:
            return False
    
    return pipeline.should_retrain(...)
```

### Issue: Model Performance Not Improving

**Problem:** New models don't improve over baseline

**Solution:**
```python
# 1. Check data quality
validate_training_data()

# 2. Increase training samples
pipeline.min_samples_retrain = 5000

# 3. Adjust comparison threshold
comparison = pipeline.compare_models(
    new_version,
    primary_metric="f1"  # Try different metric
)

# 4. Ensemble with previous models
if not comparison["is_better"]:
    # Use ensemble instead
    deploy_ensemble([new_version, baseline_version])
```

### Issue: Drift False Positives

**Problem:** Drift detected but data hasn't actually changed

**Solution:**
```python
# Use multiple drift detection methods
from scipy import stats

def validate_drift(current_data, baseline_data):
    """Validate drift with statistical test."""
    
    # Kolmogorov-Smirnov test
    statistic, pvalue = stats.ks_2samp(current_data, baseline_data)
    
    if pvalue < 0.05:
        return True  # Significant drift
    else:
        return False  # No significant drift
```

## Integration with A/B Testing

Combine continuous learning with A/B testing:

```python
from codex_ml.training.ab_testing import ABTestManager, ABTestConfig

def retrain_with_ab_test(new_data, drift_score):
    """Retrain and A/B test new model."""
    
    # 1. Retrain
    new_version = pipeline.retrain(...)
    
    # 2. Setup A/B test
    config = ABTestConfig(
        experiment_name=f"continuous_learning_{new_version.version}",
        control_variant=registry.get_latest().version,
        treatment_variants=[new_version.version],
        traffic_split={
            registry.get_latest().version: 0.9,
            new_version.version: 0.1
        },
        primary_metric="accuracy"
    )
    
    ab_test = ABTestManager(config)
    
    # 3. Run A/B test
    for _ in range(1000):  # 1000 samples
        variant = select_variant(config.traffic_split)
        result = run_inference(variant)
        ab_test.record_result(variant, result)
    
    # 4. Determine winner
    if ab_test.is_significant():
        winner = ab_test.get_winner()
        
        if winner == new_version.version:
            # Gradual rollout
            ab_test.gradual_rollout(winner, steps=5)
            pipeline.deploy_model(new_version)
        else:
            pipeline.rollback()
```

## Production Deployment

### 1. Kubernetes Deployment

```yaml
# continuous-learning-job.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: continuous-learning
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: continuous-learning
            image: codex-ml:latest
            command: ["python", "scripts/continuous_learning.py"]
            env:
            - name: DRIFT_THRESHOLD
              value: "0.15"
            - name: MIN_SAMPLES
              value: "1000"
```

### 2. Monitoring

```python
# Setup Prometheus metrics
from prometheus_client import Gauge

drift_gauge = Gauge('model_drift_score', 'Current drift score')
retraining_counter = Counter('model_retraining_total', 'Total retraining events')
accuracy_gauge = Gauge('model_accuracy', 'Production model accuracy')

def update_metrics():
    drift_gauge.set(monitor.get_max_drift())
    accuracy_gauge.set(get_production_accuracy())
```

## Summary

**Key Points:**
- ✅ Monitor drift continuously
- ✅ Auto-retrain when thresholds exceeded
- ✅ Compare new models with baselines
- ✅ Gradual rollout for safety
- ✅ Automated rollback on degradation
- ✅ Track all experiments
- ✅ Integrate with A/B testing

**Next Steps:**
- See [A/B Testing Guide](ab_testing_guide.md) for testing strategies
- See [Production Deployment Guide](production_deployment.md) for deployment patterns
- See [API Reference](../API_REFERENCE.md) for detailed API docs
