# Experiment Management

## Overview

The experiment management capability provides comprehensive experiment tracking, logging, and reproducibility infrastructure for ML workflows including hyperparameter tracking, metric logging, artifact storage, and experiment comparison.

**Keywords**: experiment, tracking, mlflow, wandb, logging, metrics, hyperparameters, artifacts, runs, reproducibility

## Purpose

Provides experiment management through:
- **Experiment Tracking**: Log runs, parameters, and metrics
- **Hyperparameter Logging**: Track all training configurations
- **Metric Visualization**: Compare runs and visualize trends
- **Artifact Storage**: Store models, plots, and outputs
- **Reproducibility**: Record all experiment details for rerun
- **Comparison**: Compare multiple experiments side-by-side

## Architecture

### Experiment Management Layers

```
┌─────────────────────────────────────┐
│   Experiment API                    │
│   (MLflow, W&B, TensorBoard)        │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Run Manager                       │
│   (Create, track, compare runs)     │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Storage Backend                   │
│   (Local, S3, database)             │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Artifact Store                    │
│   (Models, plots, checkpoints)      │
└─────────────────────────────────────┘
```

## Configuration

### Experiment Configuration

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ExperimentConfig:
    """
    Experiment configuration.
    
    Safeguard: Validates all parameters.
    """
    # Experiment identity
    name: str
    project: str = "codex-ml"
    
    # Tracking backend
    tracking_uri: str = "mlruns"
    artifact_location: Optional[str] = None
    
    # Tags and metadata
    tags: Dict[str, str] = None
    description: str = ""
    
    # Reproducibility
    random_seed: int = 42
    
    def __post_init__(self):
        """Validate configuration."""
        if not self.name:
            raise ValueError("Experiment name is required")
        if self.tags is None:
            self.tags = {}
```

### YAML Configuration

```yaml
# config/experiment.yaml
experiment:
  name: training-experiment
  project: codex-ml
  
tracking:
  backend: mlflow
  uri: http://localhost:5000
  artifact_location: s3://bucket/artifacts

logging:
  log_frequency: 100  # steps
  log_system_metrics: true
  
artifacts:
  save_model: true
  save_plots: true
  save_config: true

reproducibility:
  random_seed: 42
  log_git_hash: true
  log_environment: true
```

## Implementation

### Experiment Tracker

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
import json
import datetime

class ExperimentTracker(ABC):
    """
    Abstract base class for experiment tracking.
    
    Safeguard: Defines interface contract.
    """
    
    @abstractmethod
    def start_run(self, run_name: Optional[str] = None) -> str:
        """Start a new experiment run."""
        pass
    
    @abstractmethod
    def log_params(self, params: Dict[str, Any]) -> None:
        """Log hyperparameters."""
        pass
    
    @abstractmethod
    def log_metrics(self, metrics: Dict[str, float], step: int = None) -> None:
        """Log metrics."""
        pass
    
    @abstractmethod
    def log_artifact(self, path: str, artifact_path: str = None) -> None:
        """Log artifact file."""
        pass
    
    @abstractmethod
    def end_run(self) -> None:
        """End the current run."""
        pass

class LocalExperimentTracker(ExperimentTracker):
    """
    Local file-based experiment tracking.
    
    Safeguard: Validates file paths.
    Bounds: Limits metric history size.
    """
    
    def __init__(self, base_dir: str = "experiments"):
        self.base_dir = Path(base_dir)
        self.current_run = None
        self.run_dir = None
    
    def start_run(self, run_name: Optional[str] = None) -> str:
        """
        Start a new experiment run.
        
        Safeguard: Creates run directory safely.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = run_name or f"run_{timestamp}"
        
        self.run_dir = self.base_dir / run_name
        self.run_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_run = run_name
        
        # Initialize run metadata
        metadata = {
            "run_name": run_name,
            "start_time": timestamp,
            "status": "running"
        }
        (self.run_dir / "metadata.json").write_text(json.dumps(metadata))
        
        return run_name
    
    def log_params(self, params: Dict[str, Any]) -> None:
        """
        Log hyperparameters.
        
        Safeguard: Validates run is active.
        """
        if self.run_dir is None:
            raise RuntimeError("No active run. Call start_run() first.")
        
        params_file = self.run_dir / "params.json"
        existing = {}
        if params_file.exists():
            existing = json.loads(params_file.read_text())
        
        existing.update(params)
        params_file.write_text(json.dumps(existing, indent=2))
    
    def log_metrics(self, metrics: Dict[str, float], step: int = None) -> None:
        """
        Log metrics.
        
        Safeguard: Validates metric values.
        Bounds: Appends to metrics history.
        """
        if self.run_dir is None:
            raise RuntimeError("No active run")
        
        # Validate metrics
        for name, value in metrics.items():
            if not isinstance(value, (int, float)):
                raise TypeError(f"Metric {name} must be numeric")
        
        metrics_file = self.run_dir / "metrics.jsonl"
        entry = {"step": step, "metrics": metrics}
        
        with open(metrics_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def log_artifact(self, path: str, artifact_path: str = None) -> None:
        """
        Log artifact file.
        
        Safeguard: Validates source file exists.
        """
        if self.run_dir is None:
            raise RuntimeError("No active run")
        
        source = Path(path)
        if not source.exists():
            raise FileNotFoundError(f"Artifact not found: {path}")
        
        artifacts_dir = self.run_dir / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)
        
        import shutil
        dest = artifacts_dir / (artifact_path or source.name)
        shutil.copy2(source, dest)
    
    def end_run(self) -> None:
        """End the current run."""
        if self.run_dir is None:
            return
        
        # Update metadata
        metadata_file = self.run_dir / "metadata.json"
        metadata = json.loads(metadata_file.read_text())
        metadata["status"] = "completed"
        metadata["end_time"] = datetime.datetime.now().isoformat()
        metadata_file.write_text(json.dumps(metadata, indent=2))
        
        self.current_run = None
        self.run_dir = None
```

### MLflow Integration

```python
import mlflow
from typing import Dict, Any, Optional

class MLflowTracker(ExperimentTracker):
    """
    MLflow-based experiment tracking.
    
    Safeguard: Handles connection errors gracefully.
    """
    
    def __init__(self, tracking_uri: str, experiment_name: str):
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        self._run = None
    
    def start_run(self, run_name: Optional[str] = None) -> str:
        """
        Start MLflow run.
        
        Safeguard: Validates connection.
        """
        try:
            self._run = mlflow.start_run(run_name=run_name)
            return self._run.info.run_id
        except Exception as e:
            raise RuntimeError(f"Failed to start MLflow run: {e}")
    
    def log_params(self, params: Dict[str, Any]) -> None:
        """Log hyperparameters to MLflow."""
        if self._run is None:
            raise RuntimeError("No active run")
        mlflow.log_params(params)
    
    def log_metrics(self, metrics: Dict[str, float], step: int = None) -> None:
        """Log metrics to MLflow."""
        if self._run is None:
            raise RuntimeError("No active run")
        mlflow.log_metrics(metrics, step=step)
    
    def log_artifact(self, path: str, artifact_path: str = None) -> None:
        """Log artifact to MLflow."""
        if self._run is None:
            raise RuntimeError("No active run")
        mlflow.log_artifact(path, artifact_path)
    
    def end_run(self) -> None:
        """End MLflow run."""
        if self._run is not None:
            mlflow.end_run()
            self._run = None
```

## Usage Examples

### Example 1: Basic Experiment Tracking

```python
# Initialize tracker
tracker = LocalExperimentTracker("experiments")

# Start run
run_id = tracker.start_run("training-v1")

# Log hyperparameters
tracker.log_params({
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 100,
    "optimizer": "adam"
})

# Training loop with metric logging
for epoch in range(100):
    loss = train_epoch(model, data)
    
    tracker.log_metrics({
        "loss": loss,
        "epoch": epoch
    }, step=epoch)

# Save model artifact
torch.save(model.state_dict(), "model.pt")
tracker.log_artifact("model.pt")

# End run
tracker.end_run()
```

### Example 2: MLflow Tracking

```python
import mlflow

# Set tracking URI
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("codex-training")

# Start run with context manager
with mlflow.start_run(run_name="experiment-1"):
    # Log parameters
    mlflow.log_params({
        "learning_rate": 0.001,
        "batch_size": 32,
        "model_type": "transformer"
    })
    
    # Training
    for step in range(1000):
        loss = train_step()
        
        # Log metrics every 100 steps
        if step % 100 == 0:
            mlflow.log_metrics({"loss": loss}, step=step)
    
    # Log model
    mlflow.pytorch.log_model(model, "model")
    
    # Log artifacts
    mlflow.log_artifact("config.yaml")
```

### Example 3: Experiment Comparison

```python
def compare_experiments(exp_dirs: list) -> dict:
    """
    Compare multiple experiments.
    
    Safeguard: Validates experiment directories exist.
    """
    comparisons = {}
    
    for exp_dir in exp_dirs:
        path = Path(exp_dir)
        if not path.exists():
            continue
        
        # Load params
        params_file = path / "params.json"
        params = json.loads(params_file.read_text()) if params_file.exists() else {}
        
        # Load final metrics
        metrics_file = path / "metrics.jsonl"
        final_metrics = {}
        if metrics_file.exists():
            lines = metrics_file.read_text().strip().split("\n")
            if lines:
                final_metrics = json.loads(lines[-1]).get("metrics", {})
        
        comparisons[path.name] = {
            "params": params,
            "final_metrics": final_metrics
        }
    
    return comparisons

# Compare experiments
results = compare_experiments([
    "experiments/run_20241201",
    "experiments/run_20241202",
])

# Print comparison table
print("Experiment Comparison:")
for name, data in results.items():
    loss = data["final_metrics"].get("loss", "N/A")
    lr = data["params"].get("learning_rate", "N/A")
    print(f"  {name}: loss={loss}, lr={lr}")
```

### Example 4: Reproducibility Logging

```python
import subprocess
import sys
import platform

def log_environment(tracker: ExperimentTracker) -> None:
    """
    Log complete environment for reproducibility.
    
    Safeguard: Handles missing git gracefully.
    """
    env_info = {
        "python_version": sys.version,
        "platform": platform.platform(),
    }
    
    # Git info
    try:
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        env_info["git_hash"] = git_hash
        
        git_diff = subprocess.check_output(
            ["git", "diff", "--stat"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        env_info["git_dirty"] = bool(git_diff)
    except (subprocess.CalledProcessError, FileNotFoundError):
        env_info["git_hash"] = "unknown"
    
    # Package versions
    try:
        import torch
        env_info["torch_version"] = torch.__version__
    except ImportError:
        pass
    
    tracker.log_params(env_info)

# Log environment with experiment
tracker = LocalExperimentTracker()
tracker.start_run("reproducible-run")
log_environment(tracker)
```

### Example 5: Hyperparameter Sweep

```python
from itertools import product

def run_sweep(
    param_grid: dict,
    train_fn,
    tracker: ExperimentTracker
) -> list:
    """
    Run hyperparameter sweep.
    
    Safeguard: Validates param grid.
    Bounds: Limits total runs.
    """
    # Generate all combinations
    keys = list(param_grid.keys())
    values = list(param_grid.values())
    combinations = list(product(*values))
    
    # Bounds safeguard
    if len(combinations) > 100:
        raise ValueError(f"Too many combinations: {len(combinations)}")
    
    results = []
    
    for i, combo in enumerate(combinations):
        params = dict(zip(keys, combo))
        
        # Start run
        run_id = tracker.start_run(f"sweep-{i}")
        tracker.log_params(params)
        
        # Train
        metrics = train_fn(**params)
        tracker.log_metrics(metrics)
        
        # End run
        tracker.end_run()
        
        results.append({
            "run_id": run_id,
            "params": params,
            "metrics": metrics
        })
    
    return results

# Example sweep
param_grid = {
    "learning_rate": [0.001, 0.0001],
    "batch_size": [16, 32, 64],
    "hidden_size": [128, 256]
}

results = run_sweep(param_grid, train_model, tracker)
best_run = min(results, key=lambda x: x["metrics"]["loss"])
print(f"Best run: {best_run['run_id']}")
```

## Safeguards

### Data Validation

```python
def validate_metric(name: str, value: Any) -> float:
    """
    Validate metric value.
    
    Safeguard: Ensures valid numeric metrics.
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"Metric {name} must be numeric, got {type(value)}")
    
    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"Metric {name} is NaN or Inf")
    
    return float(value)
```

### Storage Safeguards

```python
MAX_ARTIFACT_SIZE = 100 * 1024 * 1024  # 100MB

def safe_log_artifact(tracker, path: str) -> None:
    """
    Log artifact with size limit.
    
    Safeguard: Prevents oversized artifacts.
    Bounds: Maximum file size limit.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(path)
    
    size = file_path.stat().st_size
    if size > MAX_ARTIFACT_SIZE:
        raise ValueError(f"Artifact too large: {size / 1024 / 1024:.1f}MB")
    
    tracker.log_artifact(path)
```

## Best Practices

1. **Log Everything**: Parameters, metrics, environment, code version
2. **Use Descriptive Names**: Clear run and experiment names
3. **Set Random Seeds**: For reproducibility
4. **Log at Regular Intervals**: Not every step, use batching
5. **Store Artifacts**: Models, plots, configs
6. **Tag Experiments**: Use tags for easy filtering
7. **Compare Runs**: Regularly review and compare results
8. **Clean Up**: Delete failed or unnecessary runs

## Troubleshooting

### Missing Runs

```bash
# Check experiment directory
ls -la experiments/

# Verify MLflow server
mlflow ui --port 5000
```

### Metric Logging Issues

```python
# Check for NaN values
if math.isnan(loss):
    print("Warning: NaN loss detected")
    
# Validate metric types
print(f"Loss type: {type(loss)}")
```

## Related Capabilities

- [Reproducibility](reproducibility.md) - Experiment reproducibility
- [Checkpointing](checkpointing.md) - Model checkpointing
- [Status Reporting](status_reporting.md) - Experiment status

## References

- MLflow Documentation: https://mlflow.org/docs/latest/
- Weights & Biases: https://docs.wandb.ai/
- TensorBoard: https://www.tensorflow.org/tensorboard
