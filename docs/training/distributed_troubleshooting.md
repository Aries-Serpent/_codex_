# Distributed Training Troubleshooting

> Guide for diagnosing and resolving distributed training initialization issues

## Overview

This guide helps troubleshoot common issues when using distributed training features, including PyTorch DDP and Hugging Face Accelerate.

## Quick Diagnostics

### Check Distributed Availability

```python
from codex_ml.distributed import is_distributed_available

if is_distributed_available():
    print("✓ Distributed training is available")
else:
    print("✗ Distributed training not available (CPU-only mode)")
```

### Check Accelerate Installation

```bash
python -c "import accelerate; print(f'Accelerate {accelerate.__version__}')"
```

### Check CUDA Availability

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA devices: {torch.cuda.device_count()}")
```

## Common Issues

### 1. ImportError: No module named 'accelerate'

**Symptom:**
```
ImportError: No module named 'accelerate'
```

**Solution:**
Install accelerate with the appropriate extras:

```bash
# For CPU-only
pip install accelerate

# For GPU with CUDA
pip install "accelerate>=0.20"

# Or install codex with training extras
pip install -e ".[train]"
```

### 2. Accelerate Version Compatibility

**Symptom:**
```
TypeError: Accelerator.__init__() got an unexpected keyword argument 'dataloader_config'
```

**Cause:**
Mixing accelerate API versions (pre-0.30 vs 0.30+).

**Solution:**
The codebase includes compatibility shims. Ensure you're using a supported version:

```bash
pip install "accelerate>=0.20,<1.0"
```

### 3. NCCL Backend Errors on CPU

**Symptom:**
```
RuntimeError: NCCL is not available on CPU-only builds
```

**Solution:**
Use the `gloo` backend for CPU-only distributed training:

```bash
export CODEX_DIST_BACKEND=gloo
```

Or in your training config:

```yaml
training:
  distributed:
    backend: gloo
```

### 4. Distributed Initialization Timeout

**Symptom:**
```
RuntimeError: Timed out initializing process group
```

**Solutions:**

1. **Check network connectivity** between nodes
2. **Increase timeout**:
   ```bash
   export NCCL_TIMEOUT=1800  # 30 minutes
   ```
3. **Verify environment variables**:
   ```bash
   echo $MASTER_ADDR
   echo $MASTER_PORT
   echo $RANK
   echo $WORLD_SIZE
   ```

### 5. Mixed Precision Errors

**Symptom:**
```
RuntimeError: expected scalar type Float but found Half
```

**Solution:**
Ensure consistent dtype usage. Disable mixed precision if needed:

```python
from accelerate import Accelerator

accelerator = Accelerator(mixed_precision="no")
```

### 6. Out of Memory (OOM) in Distributed Training

**Solutions:**

1. **Reduce batch size**:
   ```yaml
   training:
     per_device_batch_size: 1
     gradient_accumulation_steps: 8
   ```

2. **Enable gradient checkpointing**:
   ```yaml
   training:
     gradient_checkpointing: true
   ```

3. **Use CPU offloading**:
   ```python
   accelerator = Accelerator(
       cpu_offload=True,
       device_placement=True,
   )
   ```

### 7. Uneven Batch Distribution

**Symptom:**
Some GPUs idle while others process data.

**Solution:**
Ensure `even_batches=True` and `split_batches` are configured appropriately:

```python
from accelerate import Accelerator

accelerator = Accelerator(
    even_batches=True,
    split_batches=False,
)
```

## CPU-Only Fallback

The codebase is designed to gracefully fall back to CPU-only mode when distributed training is unavailable.

### Testing CPU Fallback

```python
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Hide GPUs

from codex_ml.distributed import (
    init_distributed_if_needed,
    get_rank,
    get_world_size,
)

# Should return False and provide safe defaults
assert init_distributed_if_needed() is False
assert get_rank() == 0
assert get_world_size() == 1
```

### Skip Distributed Tests

When running tests in CI or minimal environments:

```bash
pytest tests/ -k "not distributed"

# Or set environment variable
export CODEX_SKIP_DISTRIBUTED_TESTS=1
pytest tests/
```

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `CODEX_DDP` | `0` | Enable DDP mode (1=enabled) |
| `CODEX_DIST_BACKEND` | `nccl` | Distributed backend (nccl/gloo) |
| `CODEX_SKIP_DISTRIBUTED_TESTS` | `0` | Skip distributed tests |
| `MASTER_ADDR` | `localhost` | Master node address |
| `MASTER_PORT` | `29500` | Master node port |
| `RANK` | `0` | Process rank |
| `WORLD_SIZE` | `1` | Total number of processes |
| `LOCAL_RANK` | `0` | Local process rank (per node) |

## Multi-GPU Training

### Single Node, Multiple GPUs

```bash
# Using torchrun (recommended)
torchrun --nproc_per_node=2 -m codex_ml.cli.train \
    --config configs/training/base.yaml

# Using accelerate
accelerate launch --num_processes=2 -m codex_ml.cli.train \
    --config configs/training/base.yaml
```

### Multi-Node Training

```bash
# On master node (rank 0)
torchrun \
    --nproc_per_node=4 \
    --nnodes=2 \
    --node_rank=0 \
    --master_addr=master.example.com \
    --master_port=29500 \
    -m codex_ml.cli.train --config configs/training/base.yaml

# On worker node (rank 1)
torchrun \
    --nproc_per_node=4 \
    --nnodes=2 \
    --node_rank=1 \
    --master_addr=master.example.com \
    --master_port=29500 \
    -m codex_ml.cli.train --config configs/training/base.yaml
```

## Debugging Tips

### 1. Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from codex_ml.distributed import init_distributed_if_needed
init_distributed_if_needed()  # Will log detailed initialization steps
```

### 2. Check Process Group Status

```python
import torch.distributed as dist

if dist.is_initialized():
    print(f"Rank: {dist.get_rank()}/{dist.get_world_size()}")
    print(f"Backend: {dist.get_backend()}")
else:
    print("Distributed not initialized")
```

### 3. Test Communication

```python
import torch
import torch.distributed as dist

if dist.is_initialized():
    # Test all-reduce
    tensor = torch.ones(1)
    dist.all_reduce(tensor)
    assert tensor.item() == dist.get_world_size()
    print("✓ Communication test passed")
```

### 4. Monitor GPU Usage

```bash
# In a separate terminal
watch -n 1 nvidia-smi

# Or use nvtop for better visualization
nvtop
```

## Performance Optimization

### 1. Choose the Right Backend

- **NCCL**: Best for GPU-to-GPU communication
- **Gloo**: Best for CPU or mixed CPU/GPU
- **MPI**: Enterprise HPC environments

### 2. Tune Batch Size and Accumulation

```yaml
training:
  # Effective batch size = per_device * num_gpus * accumulation
  per_device_batch_size: 4
  gradient_accumulation_steps: 4
  # Effective batch = 4 * 2 GPUs * 4 = 32
```

### 3. Enable Compilation (PyTorch 2.0+)

```python
import torch

# Compile model for faster execution
model = torch.compile(model)
```

## Related Documentation

- [Accelerate Documentation](https://huggingface.co/docs/accelerate/)
- [PyTorch Distributed](https://pytorch.org/docs/stable/distributed.html)
- [LoRA Configuration](../guides/peft_configuration.md)
- [Training Guide](../training/README.md)

## Support

If issues persist:

1. Check the [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues)
2. Review the test suite in `tests/distributed/` and `tests/training/`
3. Enable debug logging and share output
4. Report the issue with environment details:

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import accelerate; print(f'Accelerate: {accelerate.__version__}')"
nvidia-smi  # If using GPU
```
