````markdown
# Minimal Experiment Tracking in `_codex_` (Scaffolding)

This document describes the *current* experiment tracking story for
`_codex_`. It is intentionally minimal and offline-only.

## 1. Files Per Run

Each training or evaluation run directory under `runs/` may contain:

- `run_manifest.yaml` – context + config snapshot
- `metrics.ndjson` – stepwise metrics, written by `MetricLogger`
- `experiment_meta.json` – experiment metadata, written by
  `ExperimentTracker`

Example layout:

```text
runs/
  train/
    train-20251127-000000-s123/
      run_manifest.yaml
      metrics.ndjson
      experiment_meta.json
  eval/
    eval-20251127-000100-s123/
      run_manifest.yaml
      metrics.ndjson
      experiment_meta.json
````

## 2. ExperimentTracker

Module:

* `codex_ml.logging.experiment`

Key pieces:

* `ExperimentMeta` dataclass
* `ExperimentTracker` class

Usage (conceptual):

```python
from codex_ml.logging.experiment import ExperimentTracker

tracker = ExperimentTracker(run_dir=run_dir, mode="train", run_id=run_dir.name)
tracker.log_experiment(
    experiment_name="my-experiment",
    labels={"source": "train_minimal", "config_path": str(cfg_path)},
)
```

If `experiment_name` is falsy (empty, None), the call is a no-op.

## 3. Integration with Minimal CLIs

The following CLIs accept `--experiment-name`:

* `codex_ml.cli.train_minimal`
* `codex_ml.cli.eval_minimal`

Example:

```bash
python -m codex_ml.cli.train_minimal \
  --config conf/minimal_train.yaml \
  --runs-dir runs \
  --seed 123 \
  --max-steps 5 \
  --experiment-name "exp-foo"

python -m codex_ml.cli.eval_minimal \
  --config conf/minimal_eval.yaml \
  --runs-dir runs \
  --seed 123 \
  --checkpoint runs/train \
  --experiment-name "exp-foo"
```

If `--experiment-name` is omitted, no `experiment_meta.json` is written
for the run.

## 4. Experiment Summary Tool

Tool:

* `tools/codex_experiment_summary.py`

Usage:

```bash
python tools/codex_experiment_summary.py \
  --runs-dir runs \
  --json-out codex_experiment_summary.json \
  --md-out codex_experiment_summary.md
```

Behavior:

* Scans `runs/train/**` and `runs/eval/**`.
* Reads:

  * `run_manifest.yaml`
  * `experiment_meta.json` (if present)
  * `metrics.ndjson` (last line only)
* Groups runs by `experiment_name` (or `(unlabeled)`).
* Produces:

  * JSON summary for programmatic use.
  * Markdown summary for quick inspection.

## 5. Relationship to Gap Registry & Reproducibility

This experiment tracking layer complements:

* Gap registry:

  * Which gaps are associated with which runs.
* Reproducibility manifest:

  * `codex_reproducibility_manifest.json` can reference:

    * `codex_experiment_index.json`
    * `codex_experiment_summary.json`

Together, they provide:

* A **what** view (gaps, tasks).
* A **how** view (runs, configs, metrics).
* A **where** view (artifacts on disk).

These are deliberately kept small and local, and can be extended to
richer tracking systems in future work.

````
