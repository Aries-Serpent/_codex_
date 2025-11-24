# Artifact reference

- **Dataset cache**: `artifacts/cache/<dataset>/splits-<hash>.json` created by
  `codex_ml.codex_data.load_dataset`.
- **Experiment runs**: `artifacts/experiments/<run_id>/` containing
  `run_info.json` and `events.ndjson` logged by `codex_ml.tracking.experiments`.
- **Experiment summary**: `artifacts/experiment_summary.md` and
  `artifacts/experiment_summary.json` produced by `scripts/analyze_experiments.py`.
- **Hydra outputs**: when Hydra is present, overrides are logged under
  `.hydra/` in the working directory; the minimal fallback avoids creating
  remote references.

All paths are local-first and safe to inspect without network access.
