# Functional Training

## Overview

The **functional training** system provides a flexible, composable approach to machine learning model **training** using pure **functional programming** principles. It enables **deterministic**, **reproducible training** workflows with comprehensive **experiment tracking**, **checkpointing**, and **monitoring** capabilities.

This **functional training** framework emphasizes **reproducibility**, **validation**, and **robust** error handling throughout the **training** pipeline, making it ideal for **production** deployments requiring **deterministic** behavior and **offline** execution capabilities.

## Key Features

### Functional Programming Principles
- **Pure Functions**: **Training** functions are pure and side-effect free with **validation**
- **Composability**: **Training** components can be easily composed and reused with **safeguards**
- **Reproducibility**: **Deterministic** execution with **seed** management and **rng** control
- **Immutability**: State is immutable and explicitly passed between **training** steps

### Training Capabilities
- **Flexible Training Loops**: Customizable **training** iterations with **validation** and **monitoring**
- **Experiment Tracking**: Integration with MLflow and file-based **logging** for **reproducible** experiments
- **Checkpointing**: Automatic **checkpoint** saving with **sha256** checksums for **validation**
- **Gradient Clipping**: Configurable **gradient-clipping** for **robust** **training** stability
- **Monitoring**: Real-time system **metrics** and **telemetry** **tracking** with **safeguards**

### Data Handling
- **DataLoader Integration**: PyTorch **data-loading** support with **deterministic** batching
- **Deterministic Data Loading**: **Reproducible** data iteration with **seed** control and **validation**
- **Manifest Generation**: Data **checksums** using **sha256** for **validation** and **reproducibility**

## Architecture

The functional training system consists of several key components:

```
training/
├── functional_training.py       # Core training loop implementation
├── config.py                   # Training configuration dataclasses
└── checkpoint_manager.py       # Checkpoint persistence utilities
```

## Usage

### Basic Training Example

```python
from training.functional_training import train_functional
from torch.utils.data import DataLoader

# Create dataset and dataloader
train_dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
val_dataloader = DataLoader(val_dataset, batch_size=32, shuffle=False)

# Configure training
config = {
    "model": "bert-base-uncased",
    "epochs": 10,
    "learning_rate": 2e-5,
    "seed": 42,
    "checkpoint_dir": "./checkpoints",
    "gradient_clip_norm": 1.0,
}

# Run functional training loop
train_functional(
    model=model,
    train_dataloader=train_dataloader,
    val_dataloader=val_dataloader,
    optimizer=optimizer,
    config=config,
)
```

### Training with Experiment Tracking

```python
from training.functional_training import train_functional
import mlflow

# Enable MLflow tracking
mlflow.set_tracking_uri("./mlruns")
mlflow.set_experiment("my-experiment")

with mlflow.start_run():
    # Training configuration
    config = {
        "model": "roberta-base",
        "epochs": 20,
        "batch_size": 16,
        "learning_rate": 1e-4,
        "seed": 123,
        "mlflow_tracking": True,
    }
    
    # Run training with automatic MLflow logging
    train_functional(
        model=model,
        train_dataloader=train_loader,
        config=config,
    )
```

### Resuming from Checkpoint

```python
from training.functional_training import train_functional
from codex_ml.utils.checkpointing import load_training_checkpoint

# Load checkpoint to resume training
checkpoint_path = "./checkpoints/checkpoint_epoch_5.pt"
checkpoint = load_training_checkpoint(checkpoint_path)

# Resume training from loaded state
train_functional(
    model=model,
    train_dataloader=train_loader,
    optimizer=optimizer,
    config=config,
    resume_from_checkpoint=checkpoint,
    start_epoch=checkpoint["epoch"] + 1,
)
```

## Configuration Options

### Core Training Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `epochs` | int | 10 | Number of training epochs |
| `learning_rate` | float | 1e-4 | Optimizer learning rate |
| `batch_size` | int | 32 | Training batch size |
| `seed` | int | 42 | Random seed for reproducibility |
| `gradient_clip_norm` | float | 1.0 | Maximum gradient norm for clipping |
| `checkpoint_dir` | Path | "./checkpoints" | Directory for saving checkpoints |
| `checkpoint_frequency` | int | 1 | Save checkpoint every N epochs |

### Experiment Tracking Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mlflow_tracking` | bool | False | Enable MLflow experiment tracking |
| `file_logging` | bool | True | Enable file-based logging |
| `log_dir` | Path | "./logs" | Directory for log files |
| `telemetry_enabled` | bool | True | Enable training telemetry metrics |

### Validation Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `validation_frequency` | int | 1 | Run validation every N epochs |
| `early_stopping_patience` | int | None | Stop training after N epochs without improvement |
| `validation_metric` | str | "loss" | Metric to use for early stopping |

## Advanced Features

### Custom Loss Functions

```python
def custom_loss_fn(outputs, targets):
    """Custom loss function for training."""
    # Implement custom loss logic
    loss = torch.nn.functional.cross_entropy(outputs, targets)
    return loss

train_functional(
    model=model,
    train_dataloader=train_loader,
    loss_fn=custom_loss_fn,
    config=config,
)
```

### Custom Training Hooks

```python
def on_epoch_end_hook(epoch, metrics):
    """Hook called at the end of each epoch."""
    print(f"Epoch {epoch} completed with metrics: {metrics}")
    # Custom validation logic
    
train_functional(
    model=model,
    train_dataloader=train_loader,
    config=config,
    hooks={"on_epoch_end": on_epoch_end_hook},
)
```

### Distributed Training

```python
from torch.nn.parallel import DistributedDataParallel as DDP

# Wrap model for distributed training
model = DDP(model, device_ids=[local_rank])

train_functional(
    model=model,
    train_dataloader=train_loader,
    config=config,
    distributed=True,
    world_size=world_size,
    rank=rank,
)
```

## Reproducibility

The **functional training** system ensures **reproducibility** through **deterministic** execution and comprehensive **validation**:

1. **Seed Management**: All random number generators (**rng**) are seeded for **reproducible** results
2. **Deterministic Operations**: PyTorch **deterministic** mode enabled with **validation** checks
3. **RNG State Checkpointing**: Complete **rng** state saved in **checkpoints** with **sha256** **checksums**
4. **Data Manifests**: Input data **checksums** using **sha256** for **validation** and **reproducibility**
5. **Configuration Versioning**: **Training** configuration saved with **checkpoints** for **reproducible** execution
6. **Offline Execution**: Supports **offline** **training** with local **manifest** files and **baseline** tracking

### Reproducibility Example

```python
from codex_ml.utils.checkpointing import set_seed

# Set seed for reproducibility with validation
set_seed(42)

# Enable deterministic mode with safeguards
torch.use_deterministic_algorithms(True)

# Configure reproducible training with validation
config = {
    "seed": 42,
    "deterministic": True,
    "save_rng_state": True,
    "offline": True,  # Offline execution support
    "manifest": True,  # Generate data manifest with checksums
    "baseline": "v1.0",  # Baseline tracking
}

train_functional(model=model, train_dataloader=train_loader, config=config)
```

## Monitoring and Telemetry

### System Metrics

The training system automatically tracks:
- GPU utilization and memory
- CPU utilization
- Training throughput (examples/sec)
- Step duration and timing
- Loss and gradient statistics

### Custom Metrics

```python
def compute_custom_metrics(outputs, targets):
    """Compute custom evaluation metrics."""
    accuracy = (outputs.argmax(dim=1) == targets).float().mean()
    return {"accuracy": accuracy.item()}

train_functional(
    model=model,
    train_dataloader=train_loader,
    config=config,
    metric_functions={"custom": compute_custom_metrics},
)
```

## Best Practices

1. **Always Set Seed**: Use consistent seeds for reproducibility
2. **Enable Gradient Clipping**: Prevent gradient explosion during training
3. **Checkpoint Frequently**: Save checkpoints to enable resumption
4. **Monitor Metrics**: Track validation metrics for early stopping
5. **Use Validation Data**: Regular validation prevents overfitting
6. **Log Experiments**: Use MLflow or file logging for experiment tracking
7. **Verify Reproducibility**: Run training multiple times with same seed to verify determinism

## Troubleshooting

### Training Instability

If training loss becomes NaN or diverges:
- Reduce learning rate
- Enable gradient clipping
- Check for data normalization issues
- Verify loss function implementation

### Memory Issues

If running out of GPU memory:
- Reduce batch size
- Enable gradient accumulation
- Use mixed precision training (FP16)
- Clear cache between epochs

### Slow Training

If training is slower than expected:
- Verify DataLoader workers are set appropriately
- Enable pin_memory for DataLoader
- Use profiler to identify bottlenecks
- Check GPU utilization

## Keywords

training, functional, reproducible, deterministic, experiment-tracking, checkpointing, mlflow, validation, monitoring, telemetry, gradient-clipping, seed-management, data-loading, pytorch, deep-learning

## References

- [PyTorch Training Best Practices](https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html)
- [MLflow Tracking Documentation](https://mlflow.org/docs/latest/tracking.html)
- [Reproducible ML Research](https://www.mlflow.org/docs/latest/tracking.html#automatic-logging)

## See Also

- [Unified Training](./unified_training.md) - Alternative training approach with HuggingFace Trainer
- [Checkpointing](./checkpointing.md) - Checkpoint management utilities
- [Experiment Tracking](../monitoring/experiment_tracking.md) - MLflow integration details
