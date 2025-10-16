# Codex CLI (Typer)

The `codex_cli` package exposes offline-friendly commands:

* `python -m codex_cli.app --help` — discover available commands without installing a console script.
* `python -m codex_cli.app version` — print the package version (falls back to `unknown`).
* `python -m codex_cli.app track-smoke --dir ./mlruns` — write a minimal MLflow run to a **file-backed** store.
* `python -m codex_cli.app split-smoke --seed 1337` — demonstrate deterministic dataset splitting.
* `python -m codex_cli.app checkpoint-smoke --out ./.checkpoints` — save a toy checkpoint with RNG state & metric.

> Notes
>
> * Commands are designed to be **offline** and do not start servers or require network services.
> * Optional deps: `mlflow` (for `track-smoke`), `torch` (for `split-smoke` and `checkpoint-smoke`).
