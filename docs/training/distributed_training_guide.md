# Distributed Training Guide

**Last Updated:** 2026-06-28  
**Version:** 1.0

> Comprehensive guide for setting up and running distributed training with Codex ML

---

## Overview

This guide covers distributed training strategies using:
- **PyTorch Distributed Data Parallel (DDP)** — Multi-GPU training on single/multi-node
- **Hugging Face Accelerate** — Simplified distributed training framework
- **Parameter Server** — Distributed gradient computation

## Quick Start

### Single-Node Multi-GPU Training

```python
# examples/distributed_training_simple.py
from codex.training import Trainer
from hydra import compose, initialize

initialize(config_path="../configs")
cfg = compose(config_name="train/base", 
              overrides=["training.distributed=true", "training.num_gpus=4"])

trainer = Trainer(cfg)
trainer.train()
```

Run with:
```bash
python -m torch.distributed.launch \
    --nproc_per_node=4 \
    examples/distributed_training_simple.py
```

### Multi-Node Training

```bash
# On node 0
python -m torch.distributed.launch \
    --nproc_per_node=4 \
    --nnodes=2 \
    --node_rank=0 \
    --master_addr=<MASTER_IP> \
    --master_port=29500 \
    examples/distributed_training_simple.py

# On node 1
python -m torch.distributed.launch \
    --nproc_per_node=4 \
    --nnodes=2 \
    --node_rank=1 \
    --master_addr=<MASTER_IP> \
    --master_port=29500 \
    examples/distributed_training_simple.py
```

## Training Strategies

### 1. Data Parallelism (DDP)

**Use when:** Training on multiple GPUs with same dataset replica

```python
from torch.nn.parallel import DistributedDataParallel as DDP

model = create_model()
model = model.to(rank)
model = DDP(model, device_ids=[rank])

# Training loop
for batch in dataloader:
    output = model(batch)
    loss = criterion(output, batch.labels)
    loss.backward()
    optimizer.step()
```

**Configuration:**
```yaml
# configs/train/distributed.yaml
training:
  distributed: true
  backend: "nccl"  # For GPU, use "gloo" for CPU
  num_gpus: 4
```

### 2. Gradient Accumulation

**Use when:** Batch size too large for single GPU

```python
accumulation_steps = 4
for i, batch in enumerate(dataloader):
    output = model(batch)
    loss = criterion(output, batch.labels)
    loss = loss / accumulation_steps
    loss.backward()
    
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

### 3. Mixed Precision Training

**Use when:** Reducing memory usage and increasing speed

```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for batch in dataloader:
    with autocast():
        output = model(batch)
        loss = criterion(output, batch.labels)
    
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

## Monitoring Distributed Training

### Track Rank 0 Only

```python
import torch.distributed as dist

# Only log from rank 0
if dist.get_rank() == 0:
    logger.info(f"Epoch {epoch}: loss={loss}")
    wandb.log({"loss": loss})
```

### Monitor All Ranks

```python
rank = dist.get_rank()
world_size = dist.get_world_size()

# Reduce metrics across ranks
metric_tensor = torch.tensor(metric_value, device=rank)
dist.all_reduce(metric_tensor)
metric_reduced = (metric_tensor / world_size).item()
```

## Performance Optimization

### 1. Batch Size Scaling

- Increase batch size proportionally with GPU count
- Example: 4 GPUs → 4× batch size

```yaml
# configs/train/distributed.yaml
training:
  batch_size: 128  # Per GPU
  # Effective batch size = 128 * 4 = 512
```

### 2. Learning Rate Scaling

- Scale learning rate with batch size (linear scaling rule)
- `lr_new = lr_base * (batch_size_new / batch_size_base)`

```python
base_lr = 0.001
batch_size_base = 32
batch_size_effective = 512

new_lr = base_lr * (batch_size_effective / batch_size_base)
optimizer.param_groups[0]['lr'] = new_lr
```

### 3. Gradient Compression

- Reduce communication overhead in distributed training

```python
# In backward pass
if dist.get_rank() == 0:
    # Compress gradients before sending
    compressed = compress_gradients(gradients)
    dist.all_reduce(compressed)
```

## Troubleshooting

For common issues (ImportError, CUDA errors, etc.), see:
**[Distributed Training Troubleshooting](./distributed_troubleshooting.md)**

## Resources

| Topic | File |
|-------|------|
| Troubleshooting | [Distributed Troubleshooting](./distributed_troubleshooting.md) |
| Checkpointing | [Checkpointing Guide](./checkpointing.md) |
| Reproducibility | [Reproducibility](./reproducibility.md) |

## Next Steps

1. Start with single-node training: `training.distributed=false`
2. Scale to multi-GPU: `training.num_gpus=4`
3. Add gradient accumulation for large batches
4. Enable mixed precision for speed

For more details, see the [Checkpointing Guide](./Checkpointing_Surfaces.md).
