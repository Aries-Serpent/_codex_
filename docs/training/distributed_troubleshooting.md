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
```text
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
```text
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
```text
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
```text
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
```text
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

## Safe Accelerate Initialization

The repository includes a safe initialization guard that handles CPU-only environments and missing dependencies gracefully.

### Using the Accelerate Init Guard

```python
from training.accelerate_init_guard import safe_accelerate_init

# Try to initialize accelerate with graceful fallback
result = safe_accelerate_init(cpu_fallback=True)

if result.success:
    print(f"✓ Accelerate initialized with {result.backend}")
    print(f"  World size: {result.world_size}, Rank: {result.rank}")
elif result.skip_reason:
    print(f"⊘ Skipped: {result.skip_reason}")
    # Continue with CPU-only training
else:
    print(f"✗ Error: {result.error}")
    # Handle error or fall back to CPU
```

### Diagnostic Mode

Run the guard in diagnostic mode to check your environment:

```bash
python training/accelerate_init_guard.py
```

**Output example:**
```text
============================================================
Accelerate Init Guard - Diagnostic Mode
============================================================

Distributed Environment Variables:
  MASTER_ADDR: <not set>
  MASTER_PORT: <not set>
  WORLD_SIZE: <not set>
  RANK: <not set>
  LOCAL_RANK: <not set>
  ACCELERATE_TEST: <not set>
  CUDA_VISIBLE_DEVICES: <not set>

Availability Checks:
  Accelerate available: True
  GPU available: False

Initialization Test:
  Result: AccelerateInitResult(skipped, reason=cpu_only)
```
### Skip-Safe Integration Tests

The integration tests use pytest markers to skip on CPU-only runners:

```bash
# Run all tests (skips distributed on CPU-only)
pytest tests/integration/test_distributed_init.py

# Run with GPU and ACCELERATE_TEST flag
ACCELERATE_TEST=1 pytest tests/integration/test_distributed_init.py

# Skip integration tests entirely
pytest -m "not integration"
```

### Environment Variable Reference for Safe Init

| Variable | Purpose | Example |
|----------|---------|---------|
| `ACCELERATE_TEST` | Enable GPU-gated distributed tests | `ACCELERATE_TEST=1` |
| `CUDA_VISIBLE_DEVICES` | Control GPU visibility | `CUDA_VISIBLE_DEVICES=0,1` |
| `WORLD_SIZE` | Number of processes | `WORLD_SIZE=4` |
| `RANK` | Process rank | `RANK=0` |
| `MASTER_ADDR` | Master node address | `MASTER_ADDR=localhost` |
| `MASTER_PORT` | Master node port | `MASTER_PORT=29500` |

### Common Init Guard Results

**CPU-Only Environment:**
```python
AccelerateInitResult(
    success=False,
    skip_reason='cpu_only',
    gpu_available=False,
    ...
)
```

**Accelerate Not Installed:**
```python
AccelerateInitResult(
    success=False,
    skip_reason='no_accelerate',
    accelerate_available=False,
    ...
)
```

**Successful Initialization:**
```python
AccelerateInitResult(
    success=True,
    backend='nccl',
    world_size=2,
    rank=0,
    gpu_available=True,
    ...
)
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
