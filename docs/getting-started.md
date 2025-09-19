<!-- BEGIN: CODEX_DOCS_GETTING_STARTED -->

# Getting Started (Ubuntu)

## Prerequisites

- Python 3.10+
- (Optional) Docker & Docker Compose

## Local Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r docs/requirements.txt
pip install -e '.[dev]'  # installs the pinned dev/test stack; try `uv pip sync requirements.lock`
```

Run Docs

```bash
mkdocs serve
```

## Training with LoRA and Precision Flags

The minimal trainer supports optional LoRA adapters and mixed precision.

Recommended (hyphenated flags):
```bash
python -m training.engine_hf_trainer \
  --lora-r 8 --lora-alpha 16 --lora-dropout 0.05 --precision bf16
```

`--lora-r` enables LoRA when >0. `--lora-alpha` scales the injected adapters and
`--lora-dropout` applies dropout to them. Typical values are `r` in the range
4–16, `alpha` matching `r` and dropout between `0` and `0.1`. Use `--precision`
`fp16` or `bf16` for half/mixed precision.

Typical ranges:

- `lora_r`: 4–64
- `lora_alpha`: roughly 2×`lora_r`
- `lora_dropout`: 0.0–0.3 for regularisation

Defaults live in `configs/config.yaml` under `trainer.lora_r`, `trainer.lora_alpha`, and `trainer.lora_dropout` and can be overridden per run.

Typical ranges:

- `lora_r`: 4–64
- `lora_alpha`: roughly 2×`lora_r`
- `lora_dropout`: 0.0–0.3 for regularisation

Defaults live in `configs/config.yaml` under `trainer.lora_r`, `trainer.lora_alpha`, and `trainer.lora_dropout` and can be overridden per run.

Typical ranges:

- `lora_r`: 4–64
- `lora_alpha`: roughly 2×`lora_r`
- `lora_dropout`: 0.0–0.3 for regularisation

Defaults live in `configs/config.yaml` under `trainer.lora_r`, `trainer.lora_alpha`, and `trainer.lora_dropout` and can be overridden per run.

## Checkpointing

Periodic checkpoints can be enabled via:

```bash
python -m training.engine_hf_trainer \
  --checkpoint_dir ./ckpts --save_steps 50
```

Checkpoints are written under the specified directory at the requested interval.
Each snapshot includes the current Git commit and environment metadata to aid reproducibility.

## Evaluation Runner

Use the lightweight evaluator to score a model against raw texts:

```python
from codex_ml.eval.evaluator import run_evaluator

metrics = run_evaluator("sshleifer/tiny-gpt2", ["hello world"])
print(metrics)
```

This computes token accuracy and perplexity using the utilities in `codex_ml.eval.metrics`.

<!-- END: CODEX_DOCS_GETTING_STARTED -->
