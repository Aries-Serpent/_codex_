# Evaluation Runner

`codex_ml.eval.eval_runner` evaluates saved models or generic text outputs. The
runner now streams metrics through the shared `NdjsonWriter`, so each record
matches the training schema (complete with UTC timestamps, run identifiers, and
`tags.phase = "eval"`). Use the same NDJSON summarizer CLI to consolidate rotated
shards from evaluation runs.

## Usage

```bash
python -m codex_ml.eval.eval_runner run --datasets toy_copy_task --metrics exact_match,ppl --output_dir runs/eval
```
It writes `metrics.ndjson` and `metrics.csv` with optional bootstrap confidence
intervals (`--bootstrap N`). The CSV export is filtered to the declared schema:
`run_id`, `dataset`, `split`, `phase`, `metric`, `step`, `value`, `n`,
`timestamp`, `notes`, `ci_low`, `ci_high`. Datasets load via
`codex_ml.eval.dataset_loader` and metrics come from `codex_ml.metrics.registry`.

### Configuration contract

- `EvaluationConfig.metrics_filename` controls where the NDJSON metrics log is
  written (default: `metrics.ndjson`). The summarizer (`codex-ndjson summarize`)
  can target the resulting directory directly.
- The CLI summary now includes a `metrics_path` key so scripts can locate the
  log deterministically.
- Metrics NDJSON rows reuse the training `NdjsonWriter`, ensuring the canonical
  schema (including `run_id`, `split`, `timestamp`, and `tags.phase="evaluation"`)
  and rotation-friendly formatting without additional adapters.
- Override `evaluation.split` to change the emitted split label (default
  `eval`). Supply `evaluation.run_id` when an explicit identifier is preferred;
  otherwise a deterministic hash derived from dataset path, metrics, and seed
  is used.
