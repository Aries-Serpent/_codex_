# Metrics & Experiment Tracking in `_codex_` (Scaffolding)

This document captures the current, lightweight approach to metrics logging
and experiment indexing in `_codex_`.

## 1. Metric Logging

Module: `codex_ml.logging.metrics.MetricLogger`

- Writes scalar metrics to NDJSON (`metrics.ndjson`).
- Optional system metrics (CPU %, RAM) if `psutil` is installed.
- Minimal, import-light API suitable for training / eval loops.

Example:

```python
from pathlib import Path
from codex_ml.logging.metrics import MetricLogger

run_dir = Path("runs/train/example")
with MetricLogger(run_dir / "metrics.ndjson") as logger:
    logger.log(step=0, loss=1.0)
    logger.log(step=1, loss=0.9, accuracy=0.5)
```

## 2. Experiment Index

Tool: `tools/codex_experiment_index.py`

Responsibilities:

- Scan `runs/train/**` and `runs/eval/**`.
- For each run directory, read `run_manifest.yaml` (if present) and `metrics.ndjson` (if present).
- Produce:
  - `codex_experiment_index.json`
  - `codex_experiment_index.md`

Example invocation:

```bash
python tools/codex_experiment_index.py \
  --runs-dir runs \
  --json-out codex_experiment_index.json \
  --md-out codex_experiment_index.md
```

## 3. Task Sequence Integration

`codex_task_sequence.yaml` (v0.7.0) includes a Finalization step to regenerate
the experiment index so recent runs are reflected in the summary artifacts.

## 4. Future Extensions

- Add tags/notes to run manifests.
- Link experiment index entries to richer artifacts.
- Integrate with offline-friendly tracking backends while keeping the
  `MetricLogger` API stable.
