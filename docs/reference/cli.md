# CLI reference (offline-first)

## Training

- **Primary**: `codex-train` delegates to Hydra when installed and falls back to
  a minimal local configuration when Hydra is absent. The fallback still sets up
  reproducible seeds, generates a local dataset if missing, and logs metrics to
  `artifacts/experiments/`.
- **Hydra entry**: `python -m codex_ml.cli.hydra_entry` uses the `conf/`
  directory by default. Override values with dotlist syntax, e.g.
  `model.enable_lora=true data.dataset_path=data/sample.jsonl`.

## Data loading

Use `codex_ml.codex_data.load_dataset` to read JSONL or text datasets,
shuffle deterministically, and persist cached splits under
`artifacts/cache/<dataset>/splits-<hash>.json`.

## Experiment analysis

Run `python scripts/analyze_experiments.py` to generate
`artifacts/experiment_summary.md` and `artifacts/experiment_summary.json`.
`python -m codex_ml.cli.detectors run` consumes the JSON summary as part of the
scorecard.
