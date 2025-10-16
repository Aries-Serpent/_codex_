# PR Plan — Checkpoint Resume, Deterministic Splits, Local MLflow Smoke

## Why
- **Determinism/Reproducibility**: snapshot/restore RNG (CPU & CUDA) and deterministic `random_split(..., generator=...)`.
- **Resilience**: checkpoint resume + best-K retention by metric avoids storage bloat and supports recovery.
- **Offline Tracking**: MLflow smoke with `file:` backend validates artifact/metrics logging without any network infra.

## Risks
- Torch optionality: environments without `torch` or `mlflow` must skip tests — handled via `pytest.importorskip`.
- File IO: checkpoint retention deletes older files by metric; guarded to only remove known pattern.
- CUDA RNG caveats: CUDA state is restored only if CUDA is available.

## Rollback
- Disable saving by not passing `checkpoint_dir` (trainer).
- Remove added tests/files; `rm -rf mlruns` to clear local tracking.
- Revert `requirements-dev.txt` MLflow addition if undesired.

## Tests & Docs
- `tests/test_checkpointing.py`: save/load + RNG parity.
- `tests/test_datasets_determinism.py`: seeded split reproducibility.
- `tests/test_tracking_mlflow_smoke.py`: local file store smoke.
- `nox -s tests` and `nox -s tracking_smoke`.

## References
- PyTorch RNG state CPU/CUDA getter/setters.
- `random_split(..., generator=...)` for reproducible splits.
- MLflow `file:` backend for local tracking.

## Additions in this follow-on
- **Best-K retention** now handles **NaN as worst** and breaks **ties by newer epoch**.
- **Typer CLI smoke helpers** (`codex_cli`) provide offline commands for version, MLflow smoke, deterministic split, and checkpoint smoke tests.
- **Coverage gate**: pytest enforces a 70% minimum via `--cov-fail-under=70`.

