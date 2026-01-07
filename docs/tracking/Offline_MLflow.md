# Docs: Offline MLflow — Local Params & UI

> Generated: Previous Cycle-11-05 | Author: mbaetiong

## Overview

The evaluation runner enriches MLflow runs with local parameters when `CODEX_ENABLE_MLFLOW=1` is set. This enables experiment tracking using MLflow's file backend without requiring network access or remote servers.

## Features

### Offline File Backend

- **Tracking URI**: `file:artifacts/mlruns` (default)
- **Experiment Name**: `codex_offline`
- **Network Calls**: None required
- **Storage**: Local filesystem only

### Parameters Logged

When MLflow is enabled, the runner automatically logs:

| Parameter | Source | Description |
|-----------|--------|-------------|
| `codex_git_commit` | `CODEX_GIT_COMMIT` env var | Git commit hash for reproducibility |
| `conda_env` | `CONDA_DEFAULT_ENV` env var | Conda environment name |
| `seed` | Evaluation config | Random seed value |
| `dataset_path` | Evaluation config | Absolute path to dataset file |

All parameter logging is best-effort. Failures are silently ignored to preserve offline workflows.

## Usage

### Step 1: Enable MLflow Tracking

```bash
export CODEX_ENABLE_MLFLOW=1
```text

### Step 2: (Optional) Set Environment Variables

```bash
# Capture git commit
export CODEX_GIT_COMMIT=$(git rev-parse --short HEAD)

# Capture conda environment
export CONDA_DEFAULT_ENV=$(conda info --envs | grep '*' | awk '{print $1}')
# Or if already in conda env, it's usually set automatically
```text

### Step 3: Run Evaluation

```bash
python -m codex_ml.eval.runner \
  --dataset-path data/test.jsonl \
  --metrics exact_match f1 \
  --output-dir results/eval_001 \
  --seed 42
```text

### Step 4: View Results in MLflow UI

```bash
# Launch local MLflow UI
scripts/tracking/mlflow_ui.sh

# Or manually
mlflow ui --backend-store-uri file:./mlruns --port 5000
```text

Access at: http://localhost:5000

## Example Run

```bash
# Complete workflow
export CODEX_ENABLE_MLFLOW=1
export CODEX_GIT_COMMIT=$(git rev-parse --short HEAD)

# Run evaluation
python -c "
from codex_ml.config import EvaluationConfig
from codex_ml.eval.runner import run_evaluation
from pathlib import Path
import json

dataset = Path('test.jsonl')
dataset.write_text(json.dumps({'prediction': 'hello', 'target': 'hello', 'text': 'test'}) + '\n')

cfg = EvaluationConfig(
    dataset_path=str(dataset),
    dataset_format='jsonl',
    metrics=['exact_match'],
    output_dir='eval_output',
    seed=42,
    prediction_field='prediction',
    target_field='target',
    text_field='text',
)

result = run_evaluation(cfg)
print('Metrics:', result['metrics'])
dataset.unlink()
"

# View in UI
scripts/tracking/mlflow_ui.sh
```text

## Logged Parameters in UI

After running the above example, the MLflow UI will show:

- **codex_git_commit**: `abc123d` (your current commit)
- **conda_env**: `myenv` (if set)
- **seed**: `42`
- **dataset_path**: `/absolute/path/to/test.jsonl`

## Nox Session

For quick smoke testing:

```bash
nox -s tracking_smoke
```text

This creates a local `mlruns` directory and verifies the tracking URI setup.

## Configuration

### Custom Tracking URI

Override the default tracking URI:

```bash
export MLFLOW_TRACKING_URI=file:/custom/path/mlruns
```text

The runner will still use `file:artifacts/mlruns` by default, but the `mlflow_ui.sh` script respects `MLFLOW_TRACKING_URI`.

### Custom Port for UI

```bash
# Edit mlflow_ui.sh or run manually
mlflow ui --backend-store-uri file:./mlruns --port 8080
```text

## Error Handling

All MLflow operations are wrapped in try-except blocks:

```python
try:
    import mlflow
    mlflow.set_tracking_uri("file:artifacts/mlruns")
    mlflow.start_run()
    # ... log params ...
except Exception:
    pass  # Silently ignore
```text

**Behavior**:
- If MLflow is not installed: evaluation continues normally
- If param logging fails: evaluation continues normally
- No exceptions propagated to user

## Troubleshooting

### MLflow Not Found

**Error**: `mlflow: command not found`

**Solution**:
```bash
pip install mlflow>=2.4
```text

### UI Shows No Runs

**Possible Causes**:
1. `CODEX_ENABLE_MLFLOW=1` not set
2. Evaluation not run yet
3. Wrong tracking URI

**Verification**:
```bash
# Check if mlruns directory exists
ls -la artifacts/mlruns

# Check if experiment exists
ls -la artifacts/mlruns/0

# Verify tracking URI matches
echo $MLFLOW_TRACKING_URI
```text

### Parameters Not Logged

**Possible Causes**:
1. Environment variables not set
2. MLflow import failed silently

**Verification**:
```bash
# Test MLflow import
python -c "import mlflow; print('MLflow OK')"

# Check environment
echo $CODEX_GIT_COMMIT
echo $CONDA_DEFAULT_ENV
```text

## Comparison: Local vs Remote MLflow

| Feature | Local (Offline) | Remote (Server) |
|---------|-----------------|-----------------|
| Network | None required | Required |
| Setup | Automatic | Requires server |
| Storage | Local filesystem | Server database |
| UI | `mlflow_ui.sh` | Hosted |
| Security | Local only | Authentication needed |
| Sharing | Manual (files) | Built-in |

## Best Practices

### 1. Always Set Git Commit

```bash
export CODEX_GIT_COMMIT=$(git rev-parse --short HEAD)
```text

Enables full reproducibility by tracking code version.

### 2. Use Consistent Tracking URI

Keep evaluations in same location for easy comparison:

```bash
# In .bashrc or .zshrc
export MLFLOW_TRACKING_URI=file:./mlruns
```text

### 3. Clean Old Runs

```bash
# Archive old experiments
mv mlruns mlruns_archive_$(date +%Y%m%d)

# Or delete
rm -rf mlruns
```text

### 4. Export Runs for Sharing

```bash
# MLflow export (if needed for sharing)
mlflow experiments export --experiment-id 0 --output-file experiment.json
```text

## Integration with Other Tools

### With Hydra

```bash
# Hydra config can set CODEX_ENABLE_MLFLOW
python run.py ++mlflow.enabled=true
```text

### With Jupyter

```python
import os
os.environ['CODEX_ENABLE_MLFLOW'] = '1'
os.environ['CODEX_GIT_COMMIT'] = 'notebook_run'

from codex_ml.eval.runner import run_evaluation
# ... run evaluation ...
```text

### With DVC

Track MLflow runs alongside DVC metrics:

```bash
dvc metrics show
# Compare with MLflow UI for richer details
```text

## See Also

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Evaluation Runner Guide](../reference/eval_runner.md)
- [Reproducibility Validation](../validation/Repro_Validation.md)
