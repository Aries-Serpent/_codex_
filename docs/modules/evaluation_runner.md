# Evaluation Runner

`codex_ml.eval.eval_runner` evaluates saved models or generic text outputs. When
invoked via `codex_ml.cli.codex_cli evaluate`, it now emits an aggregate metrics
NDJSON stream alongside the per-record artifacts so downstream automation can
tail or diff metrics without reparsing the summary JSON.

## Usage

```bash
python -m codex_ml.eval.eval_runner run --datasets toy_copy_task --metrics exact_match,ppl --output_dir runs/eval
```
It writes `metrics.ndjson` and `metrics.csv` with optional bootstrap confidence intervals (`--bootstrap N`). The runner loads datasets via `codex_ml.eval.dataset_loader` and metrics from `codex_ml.metrics.registry`.

### Configuration contract

- `EvaluationConfig.metrics_filename` controls where the NDJSON metrics log is
  written (default: `metrics.ndjson`).
- The CLI summary now includes a `metrics_path` key so scripts can locate the
  log deterministically.
- Metrics NDJSON rows reuse the training `NdjsonWriter`, ensuring the canonical
  schema (including `run_id`, `split`, `timestamp`, and `tags.phase="evaluation"`)
  and rotation-friendly formatting without additional adapters.
