# Pruning Log

- training evaluation loop — 2025-09-21_eval_loop.patch already present in tree; upstream code matches target hunks (no .rej generated).
- deterministic JSONL loader — 2025-09-21_deterministic_loader.patch already present; implementation exists in src/codex_ml/data/jsonl_loader.py.
- Hydra entrypoint/config — 2025-09-21_hydra_entrypoint.patch already present; CLI and config shipped previously.
- telemetry defaults — 2025-09-21_metrics_default_min.patch already active in src/codex_ml/monitoring/codex_logging.py.
