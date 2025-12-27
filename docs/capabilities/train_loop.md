# Training Loop Implementation

## Overview

**Status**: ✅ Complete - Full training loop patterns and best practices documented

This capability covers complete training loop implementations for ML models, including batch processing, gradient updates, and epoch management.

## Planned Content

This document will cover:
- **Basic Training Loop**: Single-epoch training implementation
- **Multi-Epoch Training**: Complete training with validation
- **Distributed Training**: Multi-GPU and distributed strategies
- **Mixed Precision**: AMP and gradient scaling
- **Progress Tracking**: Metrics, logging, and monitoring

## Current Implementation

Training loop patterns in _codex_ follow PyTorch best practices and are implemented across:
- **agents/** modules - Agent training implementations with various strategies
- **tests/agents/** - Training loop test examples and validation
- **Distributed support** - Multi-GPU training with DDP and FSDP
- **Mixed precision** - Automatic Mixed Precision (AMP) for faster training

### Complete Training Loop Pattern

```python
import torch
from torch.cuda.amp import autocast, GradScaler
from tqdm import tqdm

def train_loop(
    model,
    train_loader,
    val_loader,
    optimizer,
    scheduler,
    num_epochs,
    device,
    checkpoint_dir=None,
    use_amp=True,
):
    """Complete training loop with validation and checkpointing."""
    scaler = GradScaler() if use_amp else None
    best_val_loss = float('inf')
    
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        train_pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs} [Train]")
        
        for batch_idx, (inputs, targets) in enumerate(train_pbar):
            inputs, targets = inputs.to(device), targets.to(device)
            
            optimizer.zero_grad()
            
            # Mixed precision forward pass
            if use_amp:
                with autocast():
                    outputs = model(inputs)
                    loss = compute_loss(outputs, targets)
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                outputs = model(inputs)
                loss = compute_loss(outputs, targets)
                loss.backward()
                optimizer.step()
            
            train_loss += loss.item()
            train_pbar.set_postfix({"loss": loss.item()})
        
        avg_train_loss = train_loss / len(train_loader)
        
        # Validation phase
        val_loss = validate(model, val_loader, device)
        
        # Learning rate scheduling
        if scheduler:
            scheduler.step(val_loss)
        
        # Checkpoint best model
        if checkpoint_dir and val_loss < best_val_loss:
            best_val_loss = val_loss
            checkpoint_path = checkpoint_dir / f"best_model_epoch{epoch}.pt"
            save_checkpoint(model, optimizer, scheduler, epoch, checkpoint_path)
        
        print(f"Epoch {epoch+1}: train_loss={avg_train_loss:.4f}, val_loss={val_loss:.4f}")
    
    return model


def validate(model, val_loader, device):
    """Validation loop."""
    model.eval()
    val_loss = 0.0
    
    with torch.no_grad():
        for inputs, targets in val_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = compute_loss(outputs, targets)
            val_loss += loss.item()
    
    return val_loss / len(val_loader)
```

### Distributed Training Loop

```python
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

def distributed_train_loop(
    model,
    train_loader,
    optimizer,
    num_epochs,
    rank,
    world_size,
):
    """Training loop for distributed training."""
    # Wrap model with DDP
    model = model.to(rank)
    ddp_model = DDP(model, device_ids=[rank])
    
    for epoch in range(num_epochs):
        # Set epoch for distributed sampler
        train_loader.sampler.set_epoch(epoch)
        
        ddp_model.train()
        for batch in train_loader:
            inputs, targets = batch
            inputs, targets = inputs.to(rank), targets.to(rank)
            
            optimizer.zero_grad()
            outputs = ddp_model(inputs)
            loss = compute_loss(outputs, targets)
            loss.backward()
            optimizer.step()
        
        # Synchronize metrics across all processes
        if rank == 0:
            print(f"Epoch {epoch+1} complete")
        
        dist.barrier()
```

### Gradient Accumulation Pattern

```python
import torch

def train_with_gradient_accumulation(
    model,
    train_loader,
    optimizer,
    accumulation_steps=4,
    device="cuda",
):
    """Training loop with gradient accumulation for large batch sizes."""
    model.train()
    optimizer.zero_grad()
    
    for batch_idx, (inputs, targets) in enumerate(train_loader):
        inputs, targets = inputs.to(device), targets.to(device)
        
        # Forward pass
        outputs = model(inputs)
        loss = compute_loss(outputs, targets)
        
        # Scale loss by accumulation steps
        loss = loss / accumulation_steps
        loss.backward()
        
        # Update weights every N steps
        if (batch_idx + 1) % accumulation_steps == 0:
            optimizer.step()
            optimizer.zero_grad()
```

## Related Capabilities

- **functional-training**: Functional training patterns
- **experiment-management**: Training experiment tracking
- **checkpointing**: Model checkpoint management

## Example Pattern

```python
def train_epoch(model, dataloader, optimizer, device):
    """Basic training epoch implementation."""
    model.train()
    total_loss = 0.0
    
    for batch in dataloader:
        inputs, targets = batch
        inputs, targets = inputs.to(device), targets.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = compute_loss(outputs, targets)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(dataloader)
```

## Best Practices

1. **Error Handling**: Wrap training in try-except for graceful failures
   ```python
   try:
       train_loop(model, train_loader, ...)
   except KeyboardInterrupt:
       print("Training interrupted, saving checkpoint...")
       save_checkpoint(model, optimizer, epoch, "interrupted.pt")
   ```

2. **Progress Tracking**: Use tqdm for visual progress bars and logging
   - Display current loss in progress bar
   - Log metrics to tensorboard/wandb/mlflow
   - Save training curves for analysis

3. **Gradient Clipping**: Prevent exploding gradients
   ```python
   import torch
   
   torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
   ```

4. **Early Stopping**: Stop training when validation plateaus
   ```python
   if no_improvement_count >= patience:
       print("Early stopping triggered")
       break
   ```

5. **Deterministic Training**: Set seeds for reproducibility
   ```python
   import torch
   
   torch.manual_seed(42)
   torch.cuda.manual_seed_all(42)
   ```

## Integration Points

- **Checkpointing**: Save model state during training (see [checkpointing.md](checkpointing.md))
- **Experiment Tracking**: Log metrics to MLflow (see [experiment_management.md](experiment_management.md))
- **Functional Training**: Pure functional training patterns (see [functional_training.md](functional_training.md))
- **CI/CD Tests**: Training loop validation in `tests/agents/test_*_training.py`

## Performance Optimization

### Mixed Precision Training
```python
import torch
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()
with autocast():
    outputs = model(inputs)
    loss = compute_loss(outputs, targets)
scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

### DataLoader Optimization
```python
import torch
from torch.utils.data import DataLoader

train_loader = DataLoader(
    dataset,
    batch_size=32,
    num_workers=4,  # Parallel data loading
    pin_memory=True,  # Faster GPU transfer
    prefetch_factor=2,  # Pre-fetch batches
)
```

### Compilation (PyTorch 2.0+)
```python
import torch

model = torch.compile(model)  # JIT compilation for speed
```

## References

- [PyTorch Training Tutorial](https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html)
- [Mixed Precision Training](https://pytorch.org/docs/stable/amp.html)
- [Distributed Training Guide](https://pytorch.org/tutorials/intermediate/ddp_tutorial.html)
- [Functional Training](functional_training.md)
- [Experiment Management](experiment_management.md)
- [Checkpointing](checkpointing.md)
