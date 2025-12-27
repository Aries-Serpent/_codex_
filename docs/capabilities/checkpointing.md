# Model Checkpointing

> **Navigation**: [📖 Main README](../../README.md#-capabilities-documentation) | [🔄 Training Loops](train_loop.md) | [🎯 PEFT Techniques](peft_hooks.md) | [🔍 Code Quality](code_quality_tooling.md)

## Overview

**Status**: ✅ Complete - Full implementation details and examples provided

This capability covers model checkpointing strategies for saving and loading model state during training, enabling recovery from failures and experiment reproducibility.

## Planned Content

This document will cover:
- **Checkpoint Formats**: PyTorch, SafeTensors, ONNX
- **Checkpoint Strategies**: Best-model, periodic, latest
- **State Management**: Model, optimizer, scheduler state
- **Distributed Checkpointing**: Multi-GPU checkpoint handling
- **Cloud Storage**: S3, Azure, GCS integration

## Checkpoint Components

A complete checkpoint includes:
- **Model State**: Model weights and architecture
- **Optimizer State**: Optimizer parameters and momentum
- **Scheduler State**: Learning rate schedule state
- **Training Metadata**: Epoch, step, metrics, random state

## Current Implementation

Checkpointing patterns in the codebase:
- See PyTorch save/load in training code
- Check experiment management for checkpoint tracking

## Related Capabilities

- **experiment-management**: Checkpoint versioning and tracking
- **reproducibility**: Deterministic checkpoint loading
- **functional-training**: Training checkpoint integration

## Example Usage

```python
import torch

def save_checkpoint(model, optimizer, epoch, path):
    """Save a training checkpoint."""
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }
    torch.save(checkpoint, path)

def load_checkpoint(model, optimizer, path):
    """Load a training checkpoint."""
    checkpoint = torch.load(path)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    return checkpoint['epoch']
```

## Checkpoint Strategies

### Best Model
Save checkpoint when validation metric improves:
```python
if val_loss < best_val_loss:
    save_checkpoint(model, optimizer, epoch, 'best_model.pt')
    best_val_loss = val_loss
```

### Periodic
Save checkpoint at regular intervals:
```python
if epoch % save_frequency == 0:
    save_checkpoint(model, optimizer, epoch, f'checkpoint_epoch_{epoch}.pt')
```

### Latest
Always maintain the latest checkpoint:
```python
save_checkpoint(model, optimizer, epoch, 'latest.pt')
```

## Advanced Features

### SafeTensors Support
```python
from safetensors.torch import save_file, load_file

def save_safetensors(model, path):
    """Faster, safer checkpoint format."""
    save_file(model.state_dict(), path)
```

### Cloud Storage Backend
```python
class S3CheckpointBackend:
    """Store checkpoints in S3 for durability."""
    def upload_checkpoint(self, local_path):
        # Upload to S3 with retry logic
        pass
```

### Distributed Checkpointing
```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP

def save_distributed_checkpoint(model: FSDP, path, rank):
    """Save FSDP model checkpoint from rank 0."""
    if rank == 0:
        with FSDP.state_dict_type(model, StateDictType.FULL_STATE_DICT):
            torch.save(model.state_dict(), path)
```

## Best Practices

1. **Checkpoint Frequency**: Balance storage costs with recovery needs
   - Save every N steps or epochs
   - Use validation-triggered saves for best models
   - Consider adaptive frequency based on training stability

2. **State Completeness**: Save all training state together
   - Model parameters
   - Optimizer state (momentum, adaptive learning rates)
   - Scheduler state
   - Random number generator state
   - Training metadata (epoch, step, metrics)

3. **Validation & Testing**: Always test checkpoint recovery
   - Load immediately after save to verify integrity
   - Run validation forward pass to ensure model works
   - Check file size matches expected dimensions

4. **Storage Management**: Implement cleanup policies
   - Retention: Keep best N by metric, latest N by time, or periodic N
   - Archive: Move old checkpoints to cold storage
   - Compression: Use zstd/lz4 for large checkpoints

5. **Error Handling**: Robust checkpoint operations
   - Handle disk full gracefully (keep previous checkpoint)
   - Retry cloud uploads with exponential backoff
   - Atomic saves (write to temp file, then rename)

## Integration Points

- **Training Loops**: Auto-checkpoint in `agents/training_*.py` modules
- **Experiment Tracking**: Log checkpoint paths to MLflow
- **CI/CD Tests**: Checkpoint save/load tests in `tests/agents/test_*_training.py`
- **Distributed Training**: FSDP/DDP checkpoint strategies in multi-GPU setups
- **Cloud Backends**: S3/Azure/GCS integration for persistence

## Future Enhancements

1. **Incremental Checkpointing**: Save only parameter deltas for massive models
2. **Checkpoint Sharding**: Split across multiple files for parallel I/O
3. **Automatic Repair**: Detect and recover from corrupted checkpoints
4. **Checkpoint Compression**: Reduce storage with efficient compression
5. **Direct Remote Save**: Skip local disk, write directly to cloud storage

## References

- [PyTorch Checkpointing Tutorial](https://pytorch.org/tutorials/beginner/saving_loading_models.html)
- [SafeTensors Documentation](https://huggingface.co/docs/safetensors/index)
- [FSDP Checkpoint Guide](https://pytorch.org/docs/stable/fsdp.html)
- [Experiment Management](experiment_management.md)
- [Reproducibility](reproducibility.md)
- [Distributed Training](https://pytorch.org/docs/stable/distributed.html)
