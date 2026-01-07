# Docs: Optional TensorBoard Logging — Offline

> Generated: 2024-11-05 | Author: mbaetiong

## Overview

The TensorBoard logger provides simple, opt-in TensorBoard logging to improve local observability. It is disabled by default and gracefully degrades when TensorBoard is unavailable.

## Features

- **Opt-in**: Disabled by default, enable with `CODEX_ENABLE_TENSORBOARD=1`
- **Offline-friendly**: Works without network access
- **Graceful degradation**: Returns `None` if TensorBoard unavailable
- **Context-managed**: Automatic cleanup via context manager
- **Flexible backends**: Supports both `torch.utils.tensorboard` and `tensorboardX`

## Installation

TensorBoard comes with PyTorch by default:

```bash
# TensorBoard is included with PyTorch
pip install torch

# Or install standalone
pip install tensorboard
```text

## Usage

### Basic Logging

```python
from codex_ml.utils.tensorboard_logger import get_tb_writer

# Enable TensorBoard
import os
os.environ["CODEX_ENABLE_TENSORBOARD"] = "1"

# Use context manager
with get_tb_writer("runs/experiment_001") as writer:
    if writer:  # Check if writer is available
        for step in range(100):
            loss = train_step()
            writer.add_scalar("train/loss", loss, step)
```text

### In Training Loop

```python
from codex_ml.utils.tensorboard_logger import get_tb_writer

def train(config):
    with get_tb_writer(config.log_dir) as tb:
        for epoch in range(config.epochs):
            for batch_idx, batch in enumerate(dataloader):
                loss = train_batch(batch)
                
                # Log to TensorBoard if available
                if tb:
                    global_step = epoch * len(dataloader) + batch_idx
                    tb.add_scalar("train/loss", loss, global_step)
                    tb.add_scalar("train/lr", optimizer.param_groups[0]['lr'], global_step)
```text

### Checking Availability

```python
from codex_ml.utils.tensorboard_logger import is_tensorboard_available

if is_tensorboard_available():
    print("TensorBoard is available")
else:
    print("TensorBoard not installed - logging disabled")
```text

## Environment Variable

### CODEX_ENABLE_TENSORBOARD

Enable TensorBoard logging:

```bash
export CODEX_ENABLE_TENSORBOARD=1
```text

When not set or set to any other value, TensorBoard logging is disabled.

## Log Directory

### Default Location

```text
artifacts/tb_runs/
```text
### Custom Location

```python
with get_tb_writer("/custom/path/to/logs") as writer:
    if writer:
        writer.add_scalar("metric", value, step)
```text

## Viewing Logs

### Start TensorBoard UI

```bash
tensorboard --logdir artifacts/tb_runs
```text

Access at: http://localhost:6006

### Custom Port

```bash
tensorboard --logdir artifacts/tb_runs --port 8080
```text

## Logging Capabilities

### Scalars

```python
with get_tb_writer() as tb:
    if tb:
        tb.add_scalar("loss", 0.5, step=100)
        tb.add_scalars("metrics", {
            "train_loss": 0.5,
            "val_loss": 0.6
        }, step=100)
```text

### Histograms

```python
import torch

with get_tb_writer() as tb:
    if tb:
        weights = model.layer.weight.data
        tb.add_histogram("layer/weights", weights, step=100)
```text

### Images

```python
with get_tb_writer() as tb:
    if tb:
        # img should be (C, H, W) tensor
        tb.add_image("input/sample", img, step=100)
```text

### Text

```python
with get_tb_writer() as tb:
    if tb:
        tb.add_text("config", str(config), step=0)
```text

### Graphs

```python
with get_tb_writer() as tb:
    if tb:
        tb.add_graph(model, input_tensor)
```text

## Integration Examples

### With Training Script

```python
import os
from codex_ml.utils.tensorboard_logger import get_tb_writer

def main():
    # Enable TensorBoard
    os.environ["CODEX_ENABLE_TENSORBOARD"] = "1"
    
    with get_tb_writer("runs/training") as tb:
        model = create_model()
        optimizer = create_optimizer(model)
        
        for epoch in range(num_epochs):
            train_loss = train_epoch(model, optimizer)
            val_loss = validate(model)
            
            if tb:
                tb.add_scalars("epoch", {
                    "train_loss": train_loss,
                    "val_loss": val_loss
                }, epoch)
```text

### With Evaluation

```python
from codex_ml.utils.tensorboard_logger import get_tb_writer

def evaluate(model, dataset):
    with get_tb_writer("runs/evaluation") as tb:
        results = {}
        
        for metric_name, metric_fn in metrics.items():
            score = metric_fn(model, dataset)
            results[metric_name] = score
            
            if tb:
                tb.add_scalar(f"eval/{metric_name}", score, step=0)
        
        return results
```text

## Comparison with MLflow

| Feature | TensorBoard | MLflow |
|---------|-------------|--------|
| Activation | `CODEX_ENABLE_TENSORBOARD=1` | `CODEX_ENABLE_MLFLOW=1` |
| Backend | File (events) | File (runs) |
| UI | `tensorboard --logdir` | `mlflow ui` |
| Params | No | Yes |
| Metrics | Yes | Yes |
| Artifacts | Limited | Yes |
| Graphs | Yes | No |
| Images | Yes | Limited |

## Best Practices

### 1. Always Check Writer

```python
with get_tb_writer() as tb:
    if tb:  # Always check before using
        tb.add_scalar("metric", value, step)
```text

### 2. Use Descriptive Names

```python
# Good
tb.add_scalar("train/loss/ce", loss, step)
tb.add_scalar("val/accuracy/top1", acc, step)

# Bad
tb.add_scalar("loss", loss, step)
tb.add_scalar("acc", acc, step)
```text

### 3. Log at Appropriate Frequency

```python
# Log every N steps, not every step
if step % log_interval == 0:
    if tb:
        tb.add_scalar("train/loss", loss, step)
```text

### 4. Clean Up Old Runs

```bash
# Remove old TensorBoard logs
rm -rf artifacts/tb_runs/old_experiment
```text

## Troubleshooting

### TensorBoard Not Found

**Issue**: `ImportError: No module named 'tensorboard'`

**Solution**:
```bash
pip install tensorboard
# Or with PyTorch
pip install torch
```text

### No Logs Appearing

**Issue**: TensorBoard UI shows no data

**Possible Causes**:
1. `CODEX_ENABLE_TENSORBOARD` not set
2. Wrong log directory
3. Writer not flushed

**Solution**:
```python
# Ensure environment variable is set
os.environ["CODEX_ENABLE_TENSORBOARD"] = "1"

# Explicitly flush
if tb:
    tb.flush()
```text

### Permission Errors

**Issue**: Cannot write to log directory

**Solution**:
```bash
mkdir -p artifacts/tb_runs
chmod 755 artifacts/tb_runs
```text

## See Also

- [TensorBoard Documentation](https://www.tensorflow.org/tensorboard)
- [PyTorch TensorBoard Tutorial](https://pytorch.org/docs/stable/tensorboard.html)
- [MLflow Offline Guide](Offline_MLflow.md)
