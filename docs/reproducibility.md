# Reproducibility Guide

This project is designed to run fully offline. Follow the checklist below to
reproduce experiments deterministically:

1. **Seeds**
   - Every training/evaluation entrypoint accepts a `seed` parameter. Leave it at
default (`1234`) or set explicitly to guarantee determinism.
   - The training loop invokes `set_reproducible()` which seeds Python, NumPy and
     PyTorch (CPU + CUDA) and configures deterministic kernels when available.

2. **Environment capture**
   - Running `codex_ml.train_loop.run_training` or the Hydra CLI automatically
     records `environment.json`, `environment.ndjson` and `pip-freeze.txt` in the
     artifacts directory.
   - For ad-hoc runs invoke `python -m codex_ml.cli.train` and inspect the
     generated Hydra output directory under `outputs/`.

3. **Dataset checksums**
   - All dataset loaders write a checksum manifest when caching (see
     `artifacts/data_cache/`).
   - To capture additional files use `record_dataset_checksums([...], path)` from
     `codex_ml.utils.repro`.

4. **Checkpoints & resume**
   - The training loop saves per-epoch checkpoints under
     `artifacts/checkpoints/<model>/epoch_xxxx/` with metadata containing the
     epoch, global step, seed and git revision.
   - Resume by passing `checkpoint_dir=...` and `resume=true` via Hydra or the
     Python API.

5. **Experiment tracking**
   - Set `MLFLOW_ENABLE=1` (and optionally `WANDB_ENABLE=1`) before running to
     log metrics/artifacts under `artifacts/mlruns` and `artifacts/wandb`.
   - These integrations run in offline mode by default; no network connection is
     required.

6. **Configuration snapshots**
   - Hydra stores the resolved configuration (including overrides) alongside each
     run in `<hydra_run_dir>/.hydra/`. Archive these for long-term provenance.

By combining deterministic seeds, cached datasets, saved checkpoints and the
recorded environment manifests you can recreate any training or evaluation run
exactly.
