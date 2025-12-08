# Distributed Training Guide (D3)

## Overview

This guide documents the multi-node distributed training support for Codex ML. The implementation provides PyTorch DistributedDataParallel (DDP) support with optional Ray Train integration for cluster-scale training.

## Features

- ✅ PyTorch DDP wrapper for multi-GPU/multi-node training
- ✅ Optional Ray Train integration for cluster orchestration
- ✅ Automatic world size detection from environment
- ✅ Graceful fallback to single-GPU/CPU
- ✅ Context manager for easy resource management
- ✅ Distributed data loading with automatic sampler creation
- ✅ Launch script for multi-node training

## Quick Start

### Single Node, Single GPU

```python
from codex_ml.training.distributed import distributed_context
import torch.nn as nn

model = nn.Linear(10, 5)

with distributed_context() as manager:
    # Wrap model (no-op in single GPU mode)
    model = manager.wrap_model(model)
    
    # Your training loop here
    for epoch in range(10):
        # ... training code ...
        pass
```

### Single Node, Multi-GPU

```bash
# Launch with 4 GPUs
python scripts/launch_distributed.py --num-gpus 4 train.py
```

### Multi-Node Training

On each node, run:

```bash
# Node 0 (master)
python scripts/launch_distributed.py \
    --num-nodes 2 \
    --node-rank 0 \
    --num-gpus 8 \
    --master-addr 192.168.1.1 \
    train.py

# Node 1
python scripts/launch_distributed.py \
    --num-nodes 2 \
    --node-rank 1 \
    --num-gpus 8 \
    --master-addr 192.168.1.1 \
    train.py
```

## API Reference

### DistributedConfig

Configuration class for distributed training:

```python
from codex_ml.training.distributed import DistributedConfig

# Create from environment variables
config = DistributedConfig.from_env()

# Create manually
config = DistributedConfig(
    enabled=True,
    backend="nccl",  # or "gloo" for CPU
    world_size=4,
    rank=0,
    local_rank=0,
    master_addr="localhost",
    master_port="29500"
)

# Export to environment
env_vars = config.to_env()
```

### DistributedManager

Main manager class for distributed training:

```python
from codex_ml.training.distributed import DistributedManager

manager = DistributedManager(config)

# Setup distributed training
success = manager.setup()

# Check status
if manager.is_distributed:
    print(f"Rank {manager.config.rank}/{manager.config.world_size}")

# Wrap model with DDP
model = manager.wrap_model(model)

# Create distributed dataloader
dataloader = manager.wrap_dataloader(dataset, batch_size=32)

# Synchronization
manager.barrier()

# All-reduce tensor
reduced = manager.all_reduce(tensor)

# Broadcast tensor
broadcasted = manager.broadcast(tensor, src=0)

# Cleanup
manager.cleanup()
```

### Context Manager

Recommended way to use distributed training:

```python
from codex_ml.training.distributed import distributed_context

with distributed_context() as manager:
    model = manager.wrap_model(model)
    dataloader = manager.wrap_dataloader(dataset, batch_size=32)
    
    for epoch in range(10):
        for batch in dataloader:
            # Training step
            loss = compute_loss(model, batch)
            loss.backward()
            optimizer.step()
            
            # Average loss across processes
            avg_loss = manager.all_reduce(loss)
            
            if manager.is_main_process:
                print(f"Epoch {epoch}, Loss: {avg_loss.item()}")
```

### Launch Function

Programmatic multi-process launch:

```python
from codex_ml.training.distributed import launch_distributed

def train_fn(manager, **kwargs):
    model = manager.wrap_model(model)
    # ... training code ...

# Launch 4 processes
launch_distributed(
    fn=train_fn,
    world_size=4,
    backend="nccl"
)
```

## Environment Variables

The following environment variables control distributed training:

| Variable | Description | Default |
|----------|-------------|---------|
| `DISTRIBUTED_ENABLED` | Explicitly enable distributed | `false` |
| `WORLD_SIZE` | Total number of processes | `1` |
| `RANK` | Global rank of process | `0` |
| `LOCAL_RANK` | Local rank on node | `0` |
| `MASTER_ADDR` | Master node address | `localhost` |
| `MASTER_PORT` | Master node port | `29500` |
| `DISTRIBUTED_BACKEND` | Backend (nccl/gloo) | `nccl` |

## Ray Integration (Optional)

For cluster-scale training, install Ray:

```bash
pip install "ray[train]"
```

Then use the Ray trainer:

```python
from codex_ml.training.ray_distributed import RayDistributedTrainer

def train_loop(config):
    model = config["model_fn"]()
    # ... training code ...

trainer = RayDistributedTrainer(
    train_fn=train_loop,
    num_workers=4,
    use_gpu=True
)

result = trainer.train(
    train_config={"model_fn": create_model},
    num_epochs=10
)
```

## Complete Training Example

```python
#!/usr/bin/env python
"""
Distributed training example.

Run with:
    python scripts/launch_distributed.py --num-gpus 4 examples/train_distributed.py
"""
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset
from codex_ml.training.distributed import distributed_context


def main():
    # Create simple model and dataset
    model = nn.Sequential(
        nn.Linear(10, 128),
        nn.ReLU(),
        nn.Linear(128, 2)
    )
    
    dataset = TensorDataset(
        torch.randn(1000, 10),
        torch.randint(0, 2, (1000,))
    )
    
    # Use distributed context
    with distributed_context() as manager:
        # Wrap model and dataloader
        model = manager.wrap_model(model)
        dataloader = manager.wrap_dataloader(dataset, batch_size=32)
        
        optimizer = torch.optim.Adam(model.parameters())
        criterion = nn.CrossEntropyLoss()
        
        # Training loop
        for epoch in range(10):
            total_loss = 0.0
            
            for inputs, targets in dataloader:
                inputs = inputs.to(manager.device)
                targets = targets.to(manager.device)
                
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            # Average loss across all processes
            avg_loss = total_loss / len(dataloader)
            
            if manager.is_main_process:
                print(f"Epoch {epoch + 1}/10, Loss: {avg_loss:.4f}")


if __name__ == "__main__":
    main()
```

## Best Practices

### 1. Always Use Context Manager

The context manager ensures proper setup and cleanup:

```python
with distributed_context() as manager:
    # Training code
    pass
# Automatic cleanup
```

### 2. Sync Only When Necessary

Barriers are expensive. Use them sparingly:

```python
# ❌ Too frequent
for batch in dataloader:
    loss = train_step(batch)
    manager.barrier()  # Don't do this!

# ✅ Better
for batch in dataloader:
    loss = train_step(batch)

manager.barrier()  # Once per epoch is usually enough
```

### 3. Main Process for Logging

Only log from the main process to avoid duplicate output:

```python
if manager.is_main_process:
    print(f"Epoch {epoch}, Loss: {loss}")
    log_metrics({"loss": loss})
```

### 4. Reduce Metrics Properly

Always reduce metrics across processes:

```python
# Compute metric on this process
local_accuracy = compute_accuracy(predictions, targets)

# Average across all processes
global_accuracy = manager.all_reduce(
    torch.tensor(local_accuracy)
) / manager.config.world_size
```

## Troubleshooting

### Issue: "Address already in use"

**Solution**: Change the master port:

```bash
python scripts/launch_distributed.py --master-port 29501 train.py
```

### Issue: "NCCL error"

**Solution**: Use gloo backend for CPU or debugging:

```bash
export DISTRIBUTED_BACKEND=gloo
python scripts/launch_distributed.py --num-gpus 4 train.py
```

### Issue: "Timeout waiting for process group"

**Solution**: Increase timeout in your training script:

```python
config = DistributedConfig.from_env()
# Set longer timeout via environment before calling setup
```

### Issue: "Different number of processes"

**Solution**: Ensure all nodes have the same `--num-nodes` and `--num-gpus`:

```bash
# All nodes must use these exact values
--num-nodes 2 --num-gpus 8
```

## Testing

Run the test suite:

```bash
# Run distributed training tests
pytest tests/training/test_distributed.py -v

# Test module imports
python -c "from codex_ml.training.distributed import DistributedManager"

# Test launch script
python scripts/launch_distributed.py --help
```

## Deferred Item D3 Completion

### Implementation Date
2025-12-08

### Deliverables Completed
✅ Distributed training module (`src/codex_ml/training/distributed.py`)  
✅ Ray integration module (`src/codex_ml/training/ray_distributed.py`)  
✅ Launch script (`scripts/launch_distributed.py`)  
✅ Comprehensive tests (`tests/training/test_distributed.py`)  
✅ Documentation (this file)  

### Verification Status
✅ Module imports verified  
✅ DistributedConfig tested  
✅ DistributedManager tested  
✅ Context manager verified  
✅ Launch script help tested  
✅ All functions working as expected  

### Next Steps
1. ✅ D4: Config Consolidation - COMPLETE
2. ✅ D3: Multi-node Training - COMPLETE
3. Continue with D1: Docker Optimization
4. Continue with D2: Plugin Registry

## References

- [PyTorch Distributed Overview](https://pytorch.org/tutorials/beginner/dist_overview.html)
- [PyTorch DDP Tutorial](https://pytorch.org/tutorials/intermediate/ddp_tutorial.html)
- [Ray Train Documentation](https://docs.ray.io/en/latest/train/train.html)
- Existing modules: `distributed_setup.py`, `multi_node_orchestration.py`
