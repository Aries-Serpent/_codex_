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
- `--lora-r`, `--lora-alpha`, `--lora-dropout` configure optional LoRA adapters
  - typical `lora_r` values are 4–64 with `lora_alpha` around 2×`lora_r` and dropout 0.0–0.3

Both modes log metrics to TensorBoard when `--tensorboard true` is supplied.
