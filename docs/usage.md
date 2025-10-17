# Usage Guide

## Setup

Install Codex ML with the optional extras needed for training and logging:

```bash
pip install codex-ml[ml,logging]
```

This pulls in PyTorch, Transformers, and telemetry integrations such as MLflow and W&B. All functionality works offline once the dependencies are installed.

## CLI Commands

Codex ML provides a Typer-based CLI for routine operations:

- `train` — Start a training run. Supports options like `--model-name`, `--epochs`, `--batch-size`, and `--learning-rate`. Checkpoints are written under the configured `output_dir` (defaults to `runs/unified`).
- `evaluate` — Execute evaluation routines. Use `--dry-run` to validate configuration without running and `--probe-json` to output diagnostic details.
- `resume` — Continue training from a checkpoint passed via `--checkpoint`. Specify the new total `--epochs` to control the remaining duration.
- `version` — Display the installed Codex ML version.
- `info` — Print environment information including Python, platform, and telemetry libraries.

List all commands and flags with:

```bash
codex-ml-cli --help
```

## Config Customization

Training settings can be provided inline or via configuration files:

- **CLI flags:** Every field on `UnifiedTrainingConfig` has a corresponding option. For example, `--epochs 5`, `--learning-rate 1e-4`, or `--mlflow` to enable MLflow logging.
- **YAML config:** Use `--config path/to/config.yaml` to load defaults. CLI flags override values from the file. The YAML layout mirrors `UnifiedTrainingConfig`, typically under a top-level `training:` key.

## Offline Tracking

Telemetry integrates with local storage by default:

- **MLflow** is disabled unless `--mlflow` is supplied. When enabled it logs to `./mlruns` (override with `MLFLOW_TRACKING_URI="file:/abs/path/to/mlruns"`).
- **Weights & Biases** is disabled unless `--wandb` is supplied. Set `WANDB_MODE=offline` to ensure no network calls.
- **TensorBoard** can be activated via configuration (for example `enable_tensorboard=true`). Event files live under the run directory and can be viewed with `tensorboard --logdir <output_dir>`.

Run `codex-ml-cli info` to confirm which tracking backends are available and their versions.
