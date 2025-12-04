# Metrics Core and Evaluation Tool

This document describes the lightweight metrics registry under
`src/codex_ml/metrics/core.py` and its companion evaluation script
`tools/codex_metrics_eval.py`.

## Metrics Core

The metrics core exposes a minimal registry with two built-in metrics:

- **accuracy**: proportion of matching labels and predictions
- **mse**: mean squared error over numeric labels and predictions

Additional metrics can be registered by importing the registry and calling
`register` with a `Metric` instance. The registry is dependency-light and safe
to use in offline tooling.

## Evaluation Tool

`tools/codex_metrics_eval.py` computes metrics over NDJSON/JSONL or CSV logs
containing `label` and `prediction` columns. Outputs include a JSON summary and
an optional CSV table for quick inspection.

Example usage:

```bash
python tools/codex_metrics_eval.py preds.ndjson --metrics accuracy,mse \
  --json-out codex_metrics_summary.json --csv-out codex_metrics_summary.csv
```

Inputs are parsed using `label`/`target`/`truth` for labels and
`prediction`/`pred`/`output` for predictions, making the tool tolerant to slight
schema variations.

## Integration Points

- Use the JSON output as an artifact alongside experiment runs for quick
  regression checks.
- The registry can be imported by other tools that need consistent metric
  definitions without heavier ML dependencies.
