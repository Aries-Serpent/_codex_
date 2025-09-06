# Training Engine

The training engine abstracts model optimization.

## Modes
- `hf_trainer`: wraps `transformers.Trainer` for causal language modeling.
- `custom`: a minimal deterministic loop in `training/functional_training.py`.

## Key Options
- `--engine hf_trainer|custom`
- `--max-steps` limit total updates
- `--checkpoint-dir` directory for periodic checkpoints
- `--resume-from` resume training from a checkpoint

Both modes log metrics to TensorBoard when `--tensorboard true` is supplied.
