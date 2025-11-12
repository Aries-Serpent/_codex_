## [Unreleased]

### Added
- Offline-friendly BLEU/ROUGE-L generative metrics with registry integration and
  unit tests.
- Evaluation CLI options for selecting metrics and providing prediction/target
  transforms.

### Changed
- Evaluation loop now supports text post-processing hooks to unlock generative
  metrics.
- NDJSON logger registry reuses the core logger with rotation, GPU telemetry and
  configurable size limits.

### Documentation
- Updated metrics guide and logging guide to reflect generative metrics and
  NDJSON rotation controls.

## [2025-11-09] Feature Batch 1: Metrics & MLflow Guard

### Added
- ✅ Metrics API completion: F1, BLEU, token accuracy, recall classes plus NDJSON summariser
- ✅ Guarded MLflow initialization and safe logging wrappers
- ✅ Deterministic RNG checkpoint capture/restore utilities
- ✅ Dataset schema validator CLI (`scripts/validate_dataset.py`)
- ✅ Hydra multirun sweep configuration (`configs/base/hydra_sweep.yaml`)
- ✅ Device/dtype auto-detection layer for unified training
- ✅ Unified `codex_exec` task runner CLI

### Modified
- `src/codex_ml/training/unified_training.py`: MLflow guard integration, RNG restore, device state capture
- `.pre-commit-config.yaml`: Updated bandit/gitleaks hooks and shared config
- `noxfile.py`: Coverage gate (≥70%) and security session
- `docs/quickstart.md`, `docs/repro.md`, `docs/metrics.md`, `docs/configuration/hydra_quickstart.md`: Documented new workflows

### Rollback Instructions

#### Rollback Metrics API
```bash
git checkout HEAD~1 -- src/codex_ml/metrics/
git checkout HEAD~1 -- tests/metrics/
```

#### Rollback MLflow Guard
```bash
rm src/codex_ml/logging/mlflow_guard.py
git checkout HEAD~1 -- src/codex_ml/training/unified_training.py
unset CODEX_OFFLINE_MODE
```

#### Rollback RNG Checkpoint
```bash
rm src/codex_ml/training/rng_checkpoint.py
git checkout HEAD~1 -- src/codex_ml/training/unified_training.py
```

### Test Results
- Coverage: not run (optional dependencies missing in CI-free environment)
- Tests: `pytest` (fails during collection when optional deps like torch/pydantic-settings unavailable)
- Security: not run (bandit/gitleaks require local binaries)
