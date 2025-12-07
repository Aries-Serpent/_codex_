# Production Configuration Guide

This directory contains production-ready configurations for Phase 6 MLOps integration.

## Overview

Phase 6 integrates the following MLOps capabilities into production pipelines:

1. **MLflow Tracking** - Experiment tracking and artifact management
2. **Feature Store** - Centralized feature management with versioning
3. **Data Validation** - Quality checks for critical datasets
4. **Evaluation** - Standardized model evaluation
5. **Training Enhancements** - Early stopping, schedulers, checkpointing
6. **Monitoring** - Dashboards and alerting for real-time visibility

## Configuration Files

### tracking.yaml
MLflow experiment tracking configuration.

**Key Features:**
- Offline-first design with local file storage
- Automatic artifact logging
- NDJSON fallback
- Provenance tracking (git, datasets, seeds)
- Performance monitoring

**Usage:**
```bash
# Enable MLflow tracking in training
python train.py --config configs/production/tracking.yaml
```

### features.yaml
Feature store configuration for centralized feature management.

**Key Features:**
- Local parquet-based storage
- Semantic versioning (1.0.0)
- Point-in-time retrieval
- Health monitoring with SLA tracking
- 10 initial feature groups defined

**Usage:**
```bash
# Initialize feature store
python -m codex_ml.cli.feature_store init --config configs/production/features.yaml

# Register a feature group
python -m codex_ml.cli.feature_store register user_features 1.0.0 \
  --description "User demographic features"
```

### data_validation.yaml
Data quality validation configuration.

**Key Features:**
- Multi-stage validation (load, transform, pre-training)
- Statistical checks (nulls, outliers, drift)
- Dataset-specific rules (training, validation, test, inference)
- Automated reporting (JSON, HTML, Markdown)
- Alerting on failures

**Usage:**
```bash
# Validate a dataset
python -m codex_ml.cli.validate \
  --dataset data/training.parquet \
  --config configs/production/data_validation.yaml
```

### evaluation.yaml
Standardized evaluation configuration.

**Key Features:**
- EvaluationRunner interface
- Metrics by model type (classification, regression, ranking, NLP)
- CI/CD quality gates
- Performance evaluation (latency, throughput)
- Model comparison and A/B testing support

**Usage:**
```bash
# Run evaluation
python -m codex_ml.cli.evaluate \
  --model models/latest.pt \
  --dataset data/test.parquet \
  --config configs/production/evaluation.yaml
```

### training.yaml
Training enhancements configuration.

**Key Features:**
- Early stopping (patience=5, restore best weights)
- Advanced schedulers (cosine with restarts, reduce on plateau)
- Checkpointing with retention
- Gradient clipping and accumulation
- Model-specific scheduler recommendations

**Usage:**
```bash
# Train with early stopping and scheduler
python train.py --config configs/production/training.yaml
```

### monitoring.yaml
Monitoring and alerting configuration.

**Key Features:**
- 5 dashboards (MLOps, features, data quality, training, performance)
- Multi-channel alerting (Slack, Email, PagerDuty, Log)
- 12 alert rules with severity levels
- SLA monitoring and reporting
- Health checks for critical services

**Usage:**
```bash
# Deploy monitoring dashboards
python -m codex_ml.cli.monitoring deploy-dashboards \
  --config configs/production/monitoring.yaml

# Test alerts
python -m codex_ml.cli.monitoring test-alerts --channel slack
```

## Integration Guide

### Step 1: MLflow Tracking (High Priority)

Enable MLflow tracking in your training scripts:

```python
from codex_ml.training.mlflow_integration import MLflowTracker

# Initialize tracker
tracker = MLflowTracker(
    experiment_name="production_experiments",
    tracking_uri="./mlruns"
)

# Start run
with tracker:
    # Log parameters
    tracker.log_params({"lr": 0.001, "batch_size": 32})
    
    # Training loop
    for epoch in range(num_epochs):
        # ... training code ...
        tracker.log_metrics({"loss": loss, "accuracy": acc}, step=epoch)
    
    # Log artifacts
    tracker.log_artifact("model.pt")
```

**Acceptance Criteria:**
- ✅ Training runs automatically log to MLflow when enabled
- ✅ Artifacts (models, configs, metrics) properly stored
- ✅ Offline-first design maintained
- ✅ Performance overhead <5%

### Step 2: Feature Store (High Priority)

Initialize and register feature groups:

```bash
# Initialize feature store
python -m codex_ml.cli.feature_store init --config configs/production/features.yaml

# Register feature groups
python -m codex_ml.cli.feature_store register user_features 1.0.0 -d "User demographic features"
python -m codex_ml.cli.feature_store register transaction_features 1.0.0 -d "Transaction features"
python -m codex_ml.cli.feature_store register behavioral_features 1.0.0 -d "Behavioral patterns"

# List features
python -m codex_ml.cli.feature_store list --health

# Check health
python -m codex_ml.cli.feature_store health
```

**Acceptance Criteria:**
- ✅ Feature store operational in production
- ✅ ≥5 feature groups registered and versioned
- ✅ Health monitoring running continuously
- ✅ Point-in-time retrieval functional

### Step 3: Data Validation (Medium Priority)

Integrate validation into data pipelines:

```python
from codex_ml.data.validation import DataValidator

# Load validator with config
validator = DataValidator(config_path="configs/production/data_validation.yaml")

# Validate dataset
results = validator.validate(dataset, dataset_name="training")

if not results.passed:
    # Handle validation failure
    logger.error(f"Validation failed: {results.errors}")
    raise ValidationError(results.summary)
```

**Acceptance Criteria:**
- ✅ Validation runs on all critical datasets
- ✅ Invalid data blocked from training
- ✅ Validation reports generated automatically
- ✅ Validation performance <10% overhead

### Step 4: Evaluation Standardization (Medium Priority)

Use EvaluationRunner for standardized evaluation:

```python
from codex_ml.evaluation.runner import EvaluationRunner

# Initialize runner
runner = EvaluationRunner(
    model=model,
    dataset=validation_dataset,
    config_path="configs/production/evaluation.yaml"
)

# Run evaluation
results = runner.run()

# Generate report
runner.generate_report(results, output_path="artifacts/evaluation_reports/")

# Log to MLflow
runner.log_to_tracking(results)
```

**Acceptance Criteria:**
- ✅ All models use EvaluationRunner
- ✅ Metrics logged to tracking system
- ✅ Evaluation reports generated automatically
- ✅ Evaluation added to CI/CD gates

### Step 5: Monitoring Setup (Medium Priority)

Deploy dashboards and configure alerting:

```bash
# Deploy dashboards
python -m codex_ml.cli.monitoring deploy-dashboards \
  --config configs/production/monitoring.yaml

# Configure alerts
python -m codex_ml.cli.monitoring configure-alerts \
  --config configs/production/monitoring.yaml

# Test alerts
python -m codex_ml.cli.monitoring test-alerts --channel slack
```

**Acceptance Criteria:**
- ✅ Dashboards operational
- ✅ Alerts functioning correctly
- ✅ SLA monitoring enabled
- ✅ Runbooks created for common issues

## Environment Variables

Configure these environment variables for production:

```bash
# MLflow
export MLFLOW_TRACKING_URI="file://./mlruns"
export MLFLOW_EXPERIMENT_NAME="production_experiments"

# Feature Store
export FEATURE_STORE_PATH="artifacts/features/production"

# Alerting
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
export PAGERDUTY_KEY="your-pagerduty-integration-key"

# Monitoring
export MONITORING_ENABLED="true"
```

## Backward Compatibility

All features are **opt-in** and maintain 100% backward compatibility:

- MLflow tracking: `mlflow_enabled: false` by default
- Feature store: Only used when explicitly initialized
- Data validation: `enabled: false` by default
- Evaluation: Existing evaluation code continues to work
- Monitoring: Only activates when deployed

## Performance Targets

- **MLflow Tracking**: <5% overhead
- **Data Validation**: <10% overhead
- **Feature Store**: <50ms p95 latency for retrieval
- **Evaluation**: Minimal overhead (offline process)

## Rollback Procedures

If issues arise, disable features via configuration:

```yaml
# Disable MLflow
tracking:
  mlflow:
    enabled: false

# Disable validation
data_validation:
  enabled: false

# Disable feature store
feature_store:
  enabled: false
```

Or revert to previous configuration:

```bash
# Checkout previous config
git checkout HEAD~1 configs/production/

# Restart services
python -m codex_ml.cli.monitoring restart
```

## Support

For issues or questions:
- Documentation: See `docs/` directory
- Slack: #mlops-support
- Email: mlops-team@company.com

## Next Steps

1. Review configurations and customize for your use case
2. Test in development environment
3. Run integration tests
4. Gradual rollout to production
5. Monitor adoption metrics
6. Iterate based on feedback
