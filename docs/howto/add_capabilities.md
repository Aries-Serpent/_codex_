# How-to: add capabilities safely

1. Start from the structured configs in `conf/` and extend the relevant group
   (for example, add a new file under `conf/model/` for a variant that requires
   quantization). Keep defaults explicit so sweeps are reproducible.
2. Update the `ModelConfig` dataclass in `codex_ml.codex_model` if new runtime
   knobs are needed. Avoid network fetches; point to local checkpoints or cached
   adapters.
3. Wire data requirements through `codex_ml.codex_data.DataConfig` so that split
   ratios, seeds, and cache directories remain deterministic.
4. Log new signals via `codex_ml.tracking.experiments.log_metric` to keep the
   experiment summary aligned with the audit scorecard. The `analyze_experiments`
   script will surface the metrics automatically.
5. Document the capability in `docs/reference/configs.md` and add a short
   tutorial that shows how to enable it with Hydra overrides.

These steps keep the repository offline, deterministic, and auditable.
