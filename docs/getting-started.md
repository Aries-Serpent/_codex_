<!-- BEGIN: CODEX_DOCS_GETTING_STARTED -->

# Getting Started (Ubuntu)

## Prerequisites

- Python 3.10+
- (Optional) Docker & Docker Compose

## Local Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r docs/requirements.txt
pip install -e .[dev]  # if available
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

Notes:
- --lora-r enables LoRA when > 0. Adjust --lora-alpha and --lora-dropout to tune adapter capacity and regularisation.
- Use --precision fp16 or bf16 for half/mixed precision.
- For backward compatibility, underscore variants are also accepted by some entry points:
  --lora_r, --lora_alpha, --lora_dropout.

Typical ranges:
- lora-r: 4–64
- lora-alpha: roughly 2× lora-r
- lora-dropout: 0.0–0.3 for regularisation

## Checkpointing

Periodic checkpoints can be enabled via:

```bash
python -m training.engine_hf_trainer \
  --checkpoint_dir ./ckpts --save_steps 50
```

Checkpoints are written under the specified directory at the requested interval.

## Evaluation Runner

Use the lightweight evaluator to score a model against raw texts:

```python
from codex_ml.eval.evaluator import run_evaluator

metrics = run_evaluator("sshleifer/tiny-gpt2", ["hello world"])
print(metrics)
```

This computes token accuracy and perplexity using the utilities in `codex_ml.eval.metrics`.
