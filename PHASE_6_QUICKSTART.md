# Phase 6 Integration: Quick Start Guide

**Get started with MLOps production features in under 5 minutes**

---

## 🚀 Quick Start

### 1. Enable MLflow Tracking (30 seconds)

```bash
# Option 1: Via example script
python examples/production_training_with_mlflow.py --mlflow-enabled

# Option 2: In your training code
from codex_ml.training.mlflow_integration import MLflowTracker

tracker = MLflowTracker("my_experiment")
with tracker:
    tracker.log_params({"lr": 0.001, "batch_size": 32})
    # ... training loop ...
    tracker.log_metrics({"loss": loss, "accuracy": acc}, step=epoch)
```

**View results:**
```bash
mlflow ui --backend-store-uri file://./mlruns
# Open http://localhost:5000
```

---

### 2. Register Features (2 minutes)

```bash
# Initialize feature store
python -m codex_ml.cli.feature_store init --config configs/production/features.yaml

# Register a feature group
python -m codex_ml.cli.feature_store register user_features 1.0.0 \
  --description "User demographic features"

# List features
python -m codex_ml.cli.feature_store list --health
```

---

### 3. Validate Data (1 minute)

```python
# In your data pipeline
from codex_ml.data.validation import DataValidator

validator = DataValidator(config_path="configs/production/data_validation.yaml")
results = validator.validate(dataset, dataset_name="training")

if not results.passed:
    raise ValidationError(f"Validation failed: {results.errors}")
```

---

### 4. Standardized Evaluation (1 minute)

```python
from codex_ml.evaluation.runner import EvaluationRunner

runner = EvaluationRunner(
    model=model,
    dataset=test_dataset,
    config_path="configs/production/evaluation.yaml"
)

results = runner.run()
runner.generate_report(results)
```

---

### 5. Enable Early Stopping (30 seconds)

```yaml
# In your training config
training:
  early_stopping:
    enabled: true
    monitor: "val_loss"
    patience: 5
    restore_best_weights: true
```

---

## 📋 Configuration Cheat Sheet

### MLflow Tracking
```yaml
# configs/production/tracking.yaml
tracking:
  mlflow:
    enabled: true  # false by default
    uri: "file://./mlruns"
    experiment_name: "production_experiments"
```

### Feature Store
```yaml
# configs/production/features.yaml
feature_store:
  enabled: true
  storage:
    base_path: "artifacts/features/production"
    format: "parquet"
  health_check:
    stale_threshold_hours: 48
```

### Data Validation
```yaml
# configs/production/data_validation.yaml
data_validation:
  enabled: true
  null_checks:
    null_threshold: 0.05  # Max 5% nulls
  range_checks:
    enabled: true
```

### Evaluation
```yaml
# configs/production/evaluation.yaml
evaluation:
  runner: "EvaluationRunner"
  ci_cd:
    quality_gates:
      accuracy:
        min: 0.85
```

### Training
```yaml
# configs/production/training.yaml
training:
  early_stopping:
    enabled: true
    patience: 5
  scheduler:
    type: "cosine_with_restarts"
```

### Monitoring
```yaml
# configs/production/monitoring.yaml
monitoring:
  enabled: true
  alerting:
    channels:
      slack:
        webhook_url: "${SLACK_WEBHOOK_URL}"
```

---

## 🎯 Common Use Cases

### Use Case 1: Training with Full Tracking
```bash
# Create config file: my_train.yaml
training:
  learning_rate: 0.001
  batch_size: 32
  max_steps: 1000

tracking:
  mlflow_enabled: true
  experiment_name: "my_experiment"

# Run training
python examples/production_training_with_mlflow.py \
  --config my_train.yaml \
  --mlflow-enabled
```

### Use Case 2: Data Validation Pipeline
```python
# validate_and_train.py
from codex_ml.data.validation import DataValidator
from codex_ml.training.loop import run_minimal_training

# Load and validate data
validator = DataValidator("configs/production/data_validation.yaml")
results = validator.validate(dataset, "training")

if results.passed:
    # Train model
    run_minimal_training(config, max_steps=100, run_dir="./runs")
else:
    print(f"Validation failed: {results.summary}")
```

### Use Case 3: Feature Store Integration
```python
# features_pipeline.py
from codex_ml.features.feature_store import FeatureStore

# Initialize store
store = FeatureStore("artifacts/features/production")

# Register features
store.register_feature_group(
    name="user_features",
    version="1.0.0",
    features=["age", "country", "tenure"]
)

# Retrieve features (point-in-time)
features = store.get_features(
    feature_group="user_features",
    version="1.0.0",
    timestamp="2024-01-01"
)
```

### Use Case 4: CI/CD Integration
```yaml
# .github/workflows/train.yml
name: Train Model
on: [push]

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Train model
        run: |
          python train.py --config configs/production/evaluation.yaml
      - name: Evaluate
        run: |
          python -m codex_ml.cli.evaluate \
            --model models/latest.pt \
            --dataset data/test.parquet \
            --config configs/production/evaluation.yaml
      - name: Check quality gates
        run: |
          # Fails if accuracy < 0.85
          python scripts/check_quality_gates.py
```

---

## 🔍 Monitoring Dashboard URLs

After deploying monitoring:

- **MLflow UI**: http://localhost:5000
- **Feature Health**: `artifacts/features/health_reports/`
- **Data Quality**: `artifacts/validation_reports/`
- **Training Progress**: `artifacts/metrics/`
- **Model Performance**: `artifacts/evaluation_reports/`

---

## 🆘 Troubleshooting

### MLflow not logging?
```bash
# Check if MLflow is installed
python -c "import mlflow; print(mlflow.__version__)"

# Enable in config
# tracking.mlflow.enabled: true
```

### Feature store errors?
```bash
# Initialize first
python -m codex_ml.cli.feature_store init

# Check health
python -m codex_ml.cli.feature_store health
```

### Validation failing?
```bash
# Check validation report
cat artifacts/validation_reports/latest.json

# Adjust thresholds in config
# data_validation.null_checks.null_threshold: 0.10
```

### Training not stopping early?
```yaml
# Ensure monitor metric exists
training:
  early_stopping:
    monitor: "val_loss"  # Must be logged during training
    patience: 5
```

---

## 📚 Further Reading

- **Full Documentation**: `configs/production/README.md`
- **Integration Report**: `PHASE_6_INTEGRATION_COMPLETE.md`
- **Example Scripts**: `examples/`
- **Integration Tests**: `tests/integration/test_phase6_integration.py`

---

## 🔗 Quick Links

| Feature | Config | CLI | Docs |
|---------|--------|-----|------|
| MLflow | `configs/production/tracking.yaml` | N/A | README |
| Features | `configs/production/features.yaml` | `codex_ml.cli.feature_store` | README |
| Validation | `configs/production/data_validation.yaml` | `codex_ml.cli.validate` | README |
| Evaluation | `configs/production/evaluation.yaml` | `codex_ml.cli.evaluate` | README |
| Training | `configs/production/training.yaml` | N/A | README |
| Monitoring | `configs/production/monitoring.yaml` | `codex_ml.cli.monitoring` | README |

---

## ⚡ Pro Tips

1. **Start with MLflow** - Easiest integration, immediate value
2. **Use composite writer** - Get MLflow + NDJSON simultaneously
3. **Enable validation gradually** - Start with training data only
4. **Set up alerts early** - Know when features go stale
5. **Use early stopping** - Save compute, prevent overfitting
6. **Test in dev first** - Validate configs before production
7. **Monitor adoption** - Track which features teams use
8. **Document learnings** - Share best practices with team

---

**Need help?** Check `configs/production/README.md` or open an issue.

**Ready for production?** See `PHASE_6_INTEGRATION_COMPLETE.md` for deployment checklist.
