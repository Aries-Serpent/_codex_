# _codex_: Status Update (2025-09-21)

## Repo Map Snapshot
```
CHANGELOG.md
configs/
logs/
patches/
src/
tests/
.codex/
.github/
_codex/
```

## Capability Audit Summary
| Capability | Status | Notes |
| --- | --- | --- |
| Functional training loop | Stable | Deterministic eval + telemetry defaults already integrated. |
| Data ingestion | Stable | JSONL loader provides seeded shuffle and validation splitting. |
| CLI orchestration | Available | Hydra entrypoint routes to functional training config. |
| Monitoring | Minimal | Telemetry defaults set to "min" profile for offline runs. |
| Test coverage | Partial | Targeted pytest subset executed; broader nox coverage unavailable offline. |

## High-Signal Findings
- Confirmed GitHub Actions workflows disabled via `.disabled` suffix and notice banner.
- Pending patch files already present in repository; no additional hunks required.
- Deterministic JSONL loader available under `src/codex_ml/data/jsonl_loader.py` with seeded splits.
- Functional training pipeline loads dataset configs with automatic validation partitioning.
- Hydra CLI entrypoint (`codex_ml.cli.hydra_main`) resolves config and delegates to training loop.
- Base Hydra config `configs/training/functional_base.yaml` specifies offline-safe defaults.
- Telemetry initialization defaults to `min` profile enabling TensorBoard/MLflow only.
- Local pytest run over `tests/codex_ml` validated evaluation loop wiring (2 passed).
- Added offline stubs for yaml/omegaconf/hydra/torch to satisfy quick CLI gate tests.
- Coverage session not executed because `nox` command is unavailable in offline image.
- Logged nox command failures and compileall interruption into `logs/error_captures.log` per policy.
- Generated pruning log documenting that each pending patch is already integrated upstream.
- Ensured offline environment variables (NOX_OFFLINE, WANDB_MODE, MLFLOW_TRACKING_URI, CODEX_OFFLINE) set for commands.
- Created `_codex/status` artifacts and manifest placeholder for offline audit trail.
- Verified presence of pytest configuration and pre-commit hooks for local gating.
- Repository remains on existing `work` branch per higher-priority instructions.

## Applied Patch Review
- 2025-09-21_deterministic_loader.patch — Already merged; validated deterministic loader implementation. Risk: low. Rollback: N/A. Tests: `pytest tests/codex_ml`.
- 2025-09-21_eval_loop.patch — Already merged; evaluation metrics computed within training loop. Risk: low. Rollback: N/A. Tests: `pytest tests/codex_ml`.
- 2025-09-21_hydra_entrypoint.patch — Already merged; Hydra entrypoint operational offline. Risk: low. Rollback: N/A. Tests: `pytest tests/codex_ml`.
- 2025-09-21_metrics_default_min.patch — Already merged; telemetry defaults verified. Risk: low. Rollback: N/A. Tests: `pytest tests/codex_ml`.

## Local Gates
- pytest (codex_ml subset): total=2, passed=2, skipped=0, failed=0, rate=100.00%.
- pytest (quick hooks): total=7, passed=7, skipped=0, failed=0, rate=100.00%.
- coverage: not run (nox unavailable offline); cov_src=N/A.
