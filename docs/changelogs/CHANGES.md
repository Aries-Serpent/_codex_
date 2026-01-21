## [Unreleased]

### Fixed
- Fixed whitelist parsing in `scripts/remediation/verify_conflicts.py` to correctly 
  exclude whitelisted duplicates from strict mode violations. The script now properly 
  matches module paths against the `whitelist_duplicates` entries in `.github/SHIM_INVENTORY.yaml`,
  preventing false positive violations in nightly audit runs.

### Added
- Offline-friendly BLEU/ROUGE-L generative metrics with registry integration and
  unit tests.
- Evaluation CLI options for selecting metrics and providing prediction/target
  transforms.
- Capability-audit validation now honors CODEX_SKIP_VALIDATE_CHECKOUT and has a
  regression test confirming required templates, detectors, schemas, and
  supporting scripts are present.
- Post-iteration status checklist capturing audit artifacts and capability-to-marker
  mapping.
- Comprehensive test suite for `verify_conflicts.py` in `tests/scripts/test_verify_conflicts.py`
  validating whitelist parsing logic and edge cases.

### Changed
- Evaluation loop now supports text post-processing hooks to unlock generative
  metrics.
- NDJSON logger registry reuses the core logger with rotation, GPU telemetry and
  configurable size limits.
- Capability audit validator now exits non-zero with clear messaging when required
  assets are missing or ripgrep patterns have zero hits; tests exercise both
  branches.

### Documentation
- Updated metrics guide and logging guide to reflect generative metrics and
  NDJSON rotation controls.
- Optional BitsAndBytes quantization hints in `codex_ml.models.factory.create_model` with regression tests.
- Remote checkpoint synchronisation via `codex_ml.utils.storage.FSSpecStorage` and smoke tests.
- Offline CI runner script mirroring `.github/workflows/ci.yml` and documentation under `docs/development/offline_ci.md`.
- Minimal Hydra sweep definition (`configs/sweeps/minimal.yaml`) plus `nox -s sweeps_smoke` session and helper script.
- Prompt-injection and credential redaction rules in `configs/base/safety/policy.yaml`.
- Plugin development guide summarising dataset/metric/logger registries.

### Changed
- Dataset manifest guide updated to highlight deterministic JSONL/CSV loaders.
- Checkpointing documentation expanded with remote storage workflow and test guidance.

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
```text

#### Rollback MLflow Guard
```bash
rm src/codex_ml/logging/mlflow_guard.py
git checkout HEAD~1 -- src/codex_ml/training/unified_training.py
unset CODEX_OFFLINE_MODE
```text

#### Rollback RNG Checkpoint
```bash
rm src/codex_ml/training/rng_checkpoint.py
git checkout HEAD~1 -- src/codex_ml/training/unified_training.py
```text

### Test Results
- Coverage: not run (optional dependencies missing in CI-free environment)
- Tests: `pytest` (fails during collection when optional deps like torch/pydantic-settings unavailable)
- Security: not run (bandit/gitleaks require local binaries)
