# Functional Training

## Overview

The functional training capability provides modular, composable training functions and utilities for building ML training pipelines with clean separation of concerns, enabling testable and maintainable training code.

**Keywords**: training, functional, pipeline, composable, modular, train-loop, step, epoch, batch, optimizer, scheduler

## Purpose

Provides functional training through:
- **Composable Functions**: Small, reusable training primitives
- **Pipeline Building**: Chain functions into training pipelines
- **Clean Abstraction**: Separation of data, model, and optimization
- **Testability**: Functions are pure and easy to unit test
- **Flexibility**: Mix and match components as needed

## Architecture

### Functional Training Layers

```
┌─────────────────────────────────────┐
│   Training Configuration            │
│   (Hyperparameters, scheduling)     │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Training Pipeline                 │
│   (Composed functions)              │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Training Step Functions           │
│   (Forward, backward, optimize)     │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Callbacks & Hooks                 │
│   (Logging, checkpointing)          │
└─────────────────────────────────────┘
```

## Core Concepts

### Training Step Function

```python
from typing import Dict, Tuple, Any
import torch
from torch import Tensor
from torch.nn import Module
from torch.optim import Optimizer

def training_step(
    model: Module,
    batch: Tuple[Tensor, Tensor],
    optimizer: Optimizer,
    criterion: Module,
) -> Dict[str, float]:
    """
    Execute a single training step.
    
    Safeguard: Validates model is in training mode.
    Bounds: Clips gradients to prevent explosion.
    
    Args:
        model: The neural network model.
        batch: Tuple of (inputs, targets).
        optimizer: The optimizer for parameter updates.
        criterion: Loss function.
    
    Returns:
        Dictionary with loss and metrics.
    """
    # Validation safeguard
    if not model.training:
        model.train()
    
    inputs, targets = batch
    
    # Forward pass
    optimizer.zero_grad()
    outputs = model(inputs)
    loss = criterion(outputs, targets)
    
    # Backward pass with gradient clipping safeguard
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()
    
    return {"loss": loss.item()}
```

### Epoch Function

```python
from torch.utils.data import DataLoader

def train_epoch(
    model: Module,
    dataloader: DataLoader,
    optimizer: Optimizer,
    criterion: Module,
    device: str = "cpu",
) -> Dict[str, float]:
    """
    Train for one complete epoch.
    
    Safeguard: Validates dataloader is not empty.
    Bounds: Accumulates metrics safely.
    
    Args:
        model: The neural network model.
        dataloader: DataLoader for training data.
        optimizer: The optimizer.
        criterion: Loss function.
        device: Device to train on.
    
    Returns:
        Dictionary with average epoch metrics.
    """
    model.train()
    total_loss = 0.0
    num_batches = 0
    
    # Validation safeguard
    if len(dataloader) == 0:
        raise ValueError("Dataloader is empty")
    
    for batch in dataloader:
        inputs, targets = batch
        inputs = inputs.to(device)
        targets = targets.to(device)
        
        metrics = training_step(model, (inputs, targets), optimizer, criterion)
        total_loss += metrics["loss"]
        num_batches += 1
    
    # Bounds safeguard - avoid division by zero
    avg_loss = total_loss / max(num_batches, 1)
    
    return {"loss": avg_loss, "batches": num_batches}
```

## Configuration

### Training Configuration

```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class TrainingConfig:
    """
    Configuration for functional training.
    
    Safeguard: Validates all parameters.
    """
    # Training parameters
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 1e-3
    
    # Optimization
    optimizer: str = "adam"
    scheduler: Optional[str] = None
    weight_decay: float = 0.0
    
    # Safeguards
    gradient_clip_norm: float = 1.0
    early_stopping_patience: int = 5
    
    # Checkpointing
    checkpoint_dir: str = "checkpoints"
    save_every_n_epochs: int = 1
    
    def __post_init__(self):
        """Validate configuration."""
        # Validation safeguards
        if self.epochs <= 0:
            raise ValueError("epochs must be positive")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.learning_rate <= 0:
            raise ValueError("learning_rate must be positive")
```

### YAML Configuration

```yaml
# config/training.yaml
training:
  epochs: 100
  batch_size: 64
  learning_rate: 0.001
  
  optimizer:
    name: adam
    betas: [0.9, 0.999]
    weight_decay: 0.01
  
  scheduler:
    name: cosine
    warmup_epochs: 5
    min_lr: 1e-6
  
  safeguards:
    gradient_clip_norm: 1.0
    early_stopping:
      enabled: true
      patience: 10
      min_delta: 0.001
  
  checkpointing:
    enabled: true
    directory: checkpoints/
    save_best_only: true
    metric: val_loss
```

## Usage Examples

### Example 1: Basic Training Loop

```python
import torch
from torch.utils.data import DataLoader, TensorDataset

# Create model and data
model = torch.nn.Linear(10, 2)
X = torch.randn(1000, 10)
y = torch.randint(0, 2, (1000,))
dataset = TensorDataset(X, y)
dataloader = DataLoader(dataset, batch_size=32)

# Setup training
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = torch.nn.CrossEntropyLoss()

# Training loop using functional approach
for epoch in range(10):
    metrics = train_epoch(model, dataloader, optimizer, criterion)
    print(f"Epoch {epoch}: loss={metrics['loss']:.4f}")
```

### Example 2: Composable Pipeline

```python
from typing import Callable, List

def compose_pipeline(*functions: Callable) -> Callable:
    """
    Compose multiple training functions into a pipeline.
    
    Safeguard: Validates all functions are callable.
    """
    for fn in functions:
        if not callable(fn):
            raise TypeError(f"{fn} is not callable")
    
    def pipeline(state: dict) -> dict:
        for fn in functions:
            state = fn(state)
        return state
    
    return pipeline

# Define pipeline stages
def setup_stage(state):
    """Initialize training state."""
    state["model"].train()
    state["epoch_loss"] = 0.0
    return state

def batch_stage(state):
    """Process a single batch."""
    # Forward pass
    outputs = state["model"](state["inputs"])
    loss = state["criterion"](outputs, state["targets"])
    
    # Backward pass
    state["optimizer"].zero_grad()
    loss.backward()
    state["optimizer"].step()
    
    state["epoch_loss"] += loss.item()
    return state

def logging_stage(state):
    """Log training metrics."""
    print(f"Loss: {state['epoch_loss']:.4f}")
    return state

# Compose pipeline
training_pipeline = compose_pipeline(setup_stage, batch_stage, logging_stage)
```

### Example 3: Training with Callbacks

```python
from abc import ABC, abstractmethod
from typing import List

class TrainingCallback(ABC):
    """Base class for training callbacks."""
    
    def on_epoch_start(self, state: dict) -> None:
        pass
    
    def on_epoch_end(self, state: dict) -> None:
        pass
    
    def on_batch_start(self, state: dict) -> None:
        pass
    
    def on_batch_end(self, state: dict) -> None:
        pass

class EarlyStoppingCallback(TrainingCallback):
    """
    Early stopping callback.
    
    Safeguard: Prevents overfitting by stopping when loss plateaus.
    """
    
    def __init__(self, patience: int = 5, min_delta: float = 0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss = float("inf")
        self.counter = 0
    
    def on_epoch_end(self, state: dict) -> None:
        loss = state.get("val_loss", state.get("loss", float("inf")))
        
        if loss < self.best_loss - self.min_delta:
            self.best_loss = loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                state["stop_training"] = True
                print(f"Early stopping triggered after {self.counter} epochs")

class GradientLoggingCallback(TrainingCallback):
    """Log gradient statistics for debugging."""
    
    def on_batch_end(self, state: dict) -> None:
        model = state["model"]
        grad_norms = []
        
        for p in model.parameters():
            if p.grad is not None:
                grad_norms.append(p.grad.norm().item())
        
        if grad_norms:
            state["grad_norm"] = sum(grad_norms) / len(grad_norms)

def train_with_callbacks(
    model: Module,
    dataloader: DataLoader,
    optimizer: Optimizer,
    criterion: Module,
    epochs: int,
    callbacks: List[TrainingCallback],
) -> Dict[str, List[float]]:
    """
    Training loop with callback support.
    
    Safeguard: Validates callbacks list.
    """
    history = {"loss": []}
    state = {
        "model": model,
        "optimizer": optimizer,
        "criterion": criterion,
        "stop_training": False,
    }
    
    for epoch in range(epochs):
        # Call epoch start callbacks
        for cb in callbacks:
            cb.on_epoch_start(state)
        
        metrics = train_epoch(model, dataloader, optimizer, criterion)
        state.update(metrics)
        
        # Call epoch end callbacks
        for cb in callbacks:
            cb.on_epoch_end(state)
        
        history["loss"].append(metrics["loss"])
        
        # Check for early stopping
        if state.get("stop_training"):
            break
    
    return history
```

### Example 4: Distributed Training

```python
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

def setup_distributed(rank: int, world_size: int) -> None:
    """
    Setup distributed training.
    
    Safeguard: Validates rank and world_size.
    Timeout: Sets initialization timeout.
    """
    if rank < 0 or rank >= world_size:
        raise ValueError(f"Invalid rank {rank} for world_size {world_size}")
    
    dist.init_process_group(
        backend="nccl",
        rank=rank,
        world_size=world_size,
        timeout=timedelta(minutes=5),  # Timeout safeguard
    )

def distributed_training_step(
    model: DDP,
    batch: Tuple[Tensor, Tensor],
    optimizer: Optimizer,
    criterion: Module,
) -> Dict[str, float]:
    """
    Distributed training step.
    
    Safeguard: Synchronizes gradients across processes.
    """
    inputs, targets = batch
    
    optimizer.zero_grad()
    outputs = model(inputs)
    loss = criterion(outputs, targets)
    loss.backward()
    optimizer.step()
    
    # All-reduce loss for logging
    dist.all_reduce(loss, op=dist.ReduceOp.SUM)
    loss = loss / dist.get_world_size()
    
    return {"loss": loss.item()}
```

### Example 5: Mixed Precision Training

```python
from torch.cuda.amp import autocast, GradScaler

def mixed_precision_step(
    model: Module,
    batch: Tuple[Tensor, Tensor],
    optimizer: Optimizer,
    criterion: Module,
    scaler: GradScaler,
) -> Dict[str, float]:
    """
    Training step with automatic mixed precision.
    
    Safeguard: Uses GradScaler to prevent underflow.
    Bounds: Clips gradients after unscaling.
    """
    inputs, targets = batch
    
    optimizer.zero_grad()
    
    # Forward pass with autocast
    with autocast():
        outputs = model(inputs)
        loss = criterion(outputs, targets)
    
    # Backward pass with scaler
    scaler.scale(loss).backward()
    
    # Unscale and clip gradients (safeguard)
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    
    # Optimizer step with scaler
    scaler.step(optimizer)
    scaler.update()
    
    return {"loss": loss.item()}
```

## Safeguards

### Training Safeguards

- **Gradient Clipping**: Prevent gradient explosion
- **Early Stopping**: Prevent overfitting
- **NaN Detection**: Stop on NaN loss values
- **Memory Monitoring**: Track GPU memory usage
- **Checkpoint Recovery**: Resume from failures

### Validation Safeguards

```python
def validate_training_state(state: dict) -> None:
    """
    Validate training state before step.
    
    Safeguard: Ensures all required components present.
    Validation: Checks for common issues.
    """
    required = ["model", "optimizer", "criterion"]
    for key in required:
        if key not in state:
            raise ValueError(f"Missing required key: {key}")
    
    # Check for NaN in model parameters
    for name, param in state["model"].named_parameters():
        if torch.isnan(param).any():
            raise ValueError(f"NaN detected in parameter: {name}")
```

### Bounds Checking

```python
def check_loss_bounds(loss: float, max_loss: float = 1e6) -> bool:
    """
    Check if loss is within acceptable bounds.
    
    Safeguard: Detects diverging training.
    Bounds: Maximum loss threshold.
    """
    if math.isnan(loss) or math.isinf(loss):
        return False
    if loss > max_loss:
        return False
    return True
```

## Best Practices

1. **Pure Functions**: Keep training functions pure when possible
2. **Small Functions**: Each function does one thing well
3. **Composition**: Build complex pipelines from simple parts
4. **State Dictionary**: Pass state through functions explicitly
5. **Callbacks**: Use callbacks for side effects (logging, checkpointing)
6. **Validation**: Validate inputs at function boundaries
7. **Gradient Clipping**: Always clip gradients for stability
8. **Early Stopping**: Prevent overfitting with patience

## Troubleshooting

### Loss Not Decreasing

```python
# Check learning rate
print(f"Current LR: {optimizer.param_groups[0]['lr']}")

# Check gradient flow
for name, param in model.named_parameters():
    if param.grad is not None:
        print(f"{name}: grad_norm={param.grad.norm():.4f}")
```

### Out of Memory

```python
# Enable gradient checkpointing
from torch.utils.checkpoint import checkpoint

def forward_with_checkpointing(model, x):
    return checkpoint(model, x)

# Clear cache periodically
torch.cuda.empty_cache()
```

### Training Instability

```python
# Lower learning rate
optimizer.param_groups[0]['lr'] *= 0.1

# Add warmup
from torch.optim.lr_scheduler import LinearLR
scheduler = LinearLR(optimizer, start_factor=0.1, total_iters=100)
```

## Integration

### PyTorch Lightning Integration

```python
import pytorch_lightning as pl

class FunctionalTrainingModule(pl.LightningModule):
    """Wrap functional training in Lightning."""
    
    def training_step(self, batch, batch_idx):
        return training_step(self, batch, self.optimizers(), self.criterion)
```

### Hydra Configuration

```yaml
# config/train.yaml
defaults:
  - model: resnet
  - optimizer: adam
  - scheduler: cosine

training:
  epochs: ${epochs}
  batch_size: ${batch_size}
```

## Related Capabilities

- [Train Loop](train_loop.md) - Complete training loop implementation
- [PEFT Hooks](peft_hooks.md) - Parameter-efficient fine-tuning
- [Checkpointing](checkpointing.md) - Model checkpointing
- [Experiment Management](experiment_management.md) - Experiment tracking

## References

- PyTorch Training: https://pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- Functional Programming in Python: https://docs.python.org/3/howto/functional.html
