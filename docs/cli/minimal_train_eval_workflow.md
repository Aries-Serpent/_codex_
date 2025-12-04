# Minimal Train/Eval CLI Workflow for `_codex_`

This guide describes a small, **local-only** train→eval flow using the
scaffolding CLIs:

- `codex_ml.cli.train_minimal`
- `codex_ml.cli.eval_minimal`

The goal is to provide a concrete, end-to-end path that ties together:

- Config files (`conf/minimal_train.yaml`, `conf/minimal_eval.yaml`)
- Run directories + manifests (`runs/`)
- The minimal training and evaluation loops

## 1. Minimal Training Run

From the repository root:

```bash
python -m codex_ml.cli.train_minimal \
  --config conf/minimal_train.yaml \
  --seed 123 \
  --runs-dir runs
```

This will:
1. Load `conf/minimal_train.yaml` (fallback to `{}` if missing).
2. Create a run directory under `runs/train/<timestamp>_seed123/`.
3. Write a `run_manifest.yaml` with context (run id, seed, mode, config path) and a snapshot of the config.
4. Invoke `codex_ml.training.loop.run_minimal_training(...)` with the config, `max_steps` (default: 10), and `run_dir`.

## 2. Minimal Evaluation Run

After (or independently of) training, run:

```bash
python -m codex_ml.cli.eval_minimal \
  --config conf/minimal_eval.yaml \
  --seed 123 \
  --runs-dir runs \
  --checkpoint runs/train
```

This will:
1. Load `conf/minimal_eval.yaml`.
2. Create a run directory under `runs/eval/<timestamp>_seed123/`.
3. Write a `run_manifest.yaml` with context and config.
4. Invoke `codex_ml.training.loop.run_minimal_evaluation(...)` with the config, checkpoint string, and run_dir.

## 3. Run Index

Each completed run appends an entry to:

- `runs/train/runs_index.txt`
- `runs/eval/runs_index.txt`

Entries are tab-separated:

```
<mode>\t<run_id>\t<run_dir>
```

## 4. Relationship to Gap & Reproducibility Tools

These CLIs integrate with:

- `codex_ml.utils.reproducibility.set_global_seed(...)` within the CLI helper.
- Reproducibility bundle manifest: run directories can be referenced from higher-level tools.
- Gap registry and ML Test Score scaffolding: tests for the CLIs live under `tests/codex_ml/` and can be tagged in the ML Test Score map as they mature.
