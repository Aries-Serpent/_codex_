# MLflow Tracking Operations Guide

**Version**: 1.0.0  
**Last Updated**: Previous Cycle-12-07  
**Owner**: ML Engineering Team

---

## Overview

This guide provides step-by-step instructions for using MLflow tracking in production training workflows.

---

## Quick Start

### Enable MLflow Tracking

```python
from codex_ml.training.mlflow_integration import MLflowTracker

# Initialize tracker
tracker = MLflowTracker(
    experiment_name="my_experiment",
    tracking_uri="./mlruns"  # or http://mlflow-server:5000
)

# Start tracking
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

### View Results

```bash
# Start MLflow UI
mlflow ui --backend-store-uri file://./mlruns

# Open browser to http://localhost:5000
```

---

## Configuration

### Development Environment

```yaml
# configs/development/tracking.yaml
tracking:
  mlflow:
    enabled: true
    uri: "file://./mlruns"
    experiment_name: "dev_experiments"
```

### Production Environment

```yaml
# configs/production/tracking.yaml
tracking:
  mlflow:
    enabled: true
    uri: "http://mlflow-server:5000"  # Centralized server
    experiment_name: "production_experiments"
```

---

## Common Operations

### 1. Start a New Experiment

```python
tracker = MLflowTracker(
    experiment_name="new_model_experiment",
    run_name="initial_baseline",
    tags={"model": "transformer", "version": "v1"}
)
```

### 2. Log Hyperparameters

```python
tracker.log_params({
    "learning_rate": 0.001,
    "batch_size": 32,
    "num_epochs": 100,
    "optimizer": "adam",
    "model_architecture": "transformer"
})
```

### 3. Log Metrics During Training

```python
for epoch in range(num_epochs):
    train_loss = train_one_epoch(model, dataloader)
    val_loss = validate(model, val_dataloader)
    
    tracker.log_metrics({
        "train_loss": train_loss,
        "val_loss": val_loss,
        "learning_rate": optimizer.param_groups[0]['lr']
    }, step=epoch)
```

### 4. Log Artifacts

```python
# Log model checkpoint
tracker.log_artifact("checkpoints/model_epoch_10.pt")

# Log configuration file
tracker.log_artifact("config.yaml")

# Log training plots
tracker.log_artifact("plots/loss_curve.png")
```

### 5. Query Past Experiments

```python
import mlflow

# Search for runs
runs = mlflow.search_runs(
    experiment_names=["production_experiments"],
    filter_string="metrics.accuracy > 0.9",
    order_by=["metrics.accuracy DESC"]
)

print(runs[["run_id", "metrics.accuracy", "params.learning_rate"]])
```

---

## Troubleshooting

### Issue: MLflow Not Logging

**Symptoms**: No runs appear in MLflow UI

**Solutions**:
1. Check if MLflow is enabled in config:
   ```yaml
   tracking.mlflow.enabled: true
   ```

2. Verify MLflow is installed:
   ```bash
   python -c "import mlflow; print(mlflow.__version__)"
   ```

3. Check tracking URI:
   ```python
   import mlflow
   print(mlflow.get_tracking_uri())
   ```

### Issue: Connection Error to MLflow Server

**Symptoms**: Cannot connect to remote MLflow server

**Solutions**:
1. Verify server is running:
   ```bash
   curl http://mlflow-server:5000/health
   ```

2. Check network connectivity:
   ```bash
   ping mlflow-server
   ```

3. Fall back to local tracking:
   ```python
   tracker = MLflowTracker(
        experiment_name="my_exp",
        tracking_uri="file://./mlruns"  # Local fallback
   )
   ```

### Issue: Performance Degradation

**Symptoms**: Training slower with MLflow enabled

**Solutions**:
1. Enable async logging:
   ```yaml
   tracking:
     mlflow:
       async_logging: true
   ```

2. Batch metrics:
   ```yaml
   tracking:
     mlflow:
       batch_metrics: true
   ```

3. Reduce logging frequency:
   ```python
   if epoch % 10 == 0:  # Log every 10 epochs
       tracker.log_metrics(metrics, step=epoch)
   ```

---

## Best Practices

### 1. Naming Conventions

- **Experiments**: Use descriptive names: `{model_type}_{dataset}_{date}`
  - Example: `transformer_squad_20251207`

- **Runs**: Include key parameters: `{variant}_{key_param}`
  - Example: `baseline_lr0.001`

- **Tags**: Use for categorization:
  ```python
  tags={
      "model_family": "transformer",
      "dataset": "squad",
      "environment": "production",
      "team": "ml_core"
  }
  ```

### 2. What to Log

**Always Log**:
- All hyperparameters
- Final metrics (accuracy, F1, etc.)
- Model checkpoints (best model)
- Configuration files
- Git commit hash

**Optionally Log**:
- Intermediate metrics (every N steps)
- Gradient norms
- Learning rate schedule
- Training plots
- Dataset samples

**Don't Log**:
- Raw training data (too large)
- Sensitive information
- Temporary files

### 3. Organization

```
mlruns/
├── experiment_1/          # Baseline models
│   ├── run_abc123/
│   └── run_def456/
├── experiment_2/          # Hyperparameter tuning
│   ├── run_ghi789/
│   └── run_jkl012/
└── experiment_3/          # Production candidates
    ├── run_mno345/
    └── run_pqr678/
```

---

## Monitoring & Alerts

### Set Up Alerts for Failed Runs

```python
# In your training script
try:
    with tracker:
        # Training code
        results = train_model()
        tracker.log_metrics(results)
except Exception as e:
    tracker.set_tags({"status": "failed", "error": str(e)})
    raise
```

### Monitor Run Duration

```python
import time

start_time = time.time()
with tracker:
    # Training
    pass

duration = time.time() - start_time
tracker.log_metrics({"duration_seconds": duration})

if duration > 3600:  # Alert if > 1 hour
    send_alert(f"Long training run: {duration}s")
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
# .github/workflows/train.yml
name: Train Model

on: [push]

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: pip install -e .
      
      - name: Train model with MLflow
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_URI }}
        run: |
          python train.py --config configs/production/tracking.yaml
      
      - name: Check model quality
        run: |
          python scripts/check_mlflow_metrics.py --min-accuracy 0.85
```

---

## FAQ

**Q: Can I use MLflow with existing training code?**  
A: Yes! MLflow integration is opt-in and backward compatible.

**Q: What's the performance overhead?**  
A: <1% with default settings, <5% with full logging.

**Q: Can I disable MLflow temporarily?**  
A: Yes, set `tracking.mlflow.enabled: false` in config.

**Q: How long are experiments retained?**  
A: Indefinitely by default. Set up retention policies as needed.

**Q: Can multiple people share experiments?**  
A: Yes, use a centralized MLflow server.

---

## Support

- **Slack**: #mlops-support
- **Email**: mlops-team@company.com
- **Documentation**: `configs/production/README.md`
- **Issues**: GitHub Issues

---

*Last reviewed: Previous Cycle-12-07*
