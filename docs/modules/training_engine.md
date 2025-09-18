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
  - defaults are configurable via `trainer.lora_r`, `trainer.lora_alpha`, `trainer.lora_dropout`

Both modes log metrics to TensorBoard when `--tensorboard true` is supplied.

## CLI integration
- Use `codex train --config <path>` to invoke the functional trainer without writing Python glue code.
- The default configuration at `configs/training/base.yaml` seeds runs, enables checkpoints, and can be extended via Hydra overrides.
- Passing `--resume-from` to the CLI replays the most recent checkpoint. Provide
  either a specific epoch directory or the run directory; the manager will
  resolve the latest snapshot automatically.
