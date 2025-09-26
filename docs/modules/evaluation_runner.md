# Evaluation Runner

`codex_ml.eval.eval_runner` evaluates saved models or generic text outputs.

## Usage

```bash
python -m codex_ml.eval.eval_runner run --datasets toy_copy_task --metrics exact_match,ppl --output_dir runs/eval
```
It writes `metrics.ndjson` and `metrics.csv` with optional bootstrap confidence intervals (`--bootstrap N`). The runner loads datasets via `codex_ml.eval.dataset_loader` and metrics from `codex_ml.metrics.registry`.
