<!-- BEGIN: CODEX_TRAIN_ARGS_DOC -->
# Training Arguments (YAML/Hydra)

- **gradient_accumulation_steps**: accumulate before optimizer step.
- **early_stopping**: enable with patience/min_delta; wire to callbacks.EarlyStopping in your trainer loop.

## Reproducibility
- Use `set_seed(seed)` in training scripts to fix RNGs across `random`, `numpy`, and `torch`; a `seeds.json` file is written under the run directory.
- Each checkpoint records `rng.json` with RNG states for Python, NumPy, and Torch (CPU & CUDA) and restores them on load.
- `CheckpointManager.resume_from` validates model and optimizer parameter shapes and raises informative errors on mismatch.
