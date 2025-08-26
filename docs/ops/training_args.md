<!-- BEGIN: CODEX_TRAIN_ARGS_DOC -->
# Training Arguments (YAML/Hydra)

- **gradient_accumulation_steps**: accumulate before optimizer step.
- **early_stopping**: enable with patience/min_delta; wire to callbacks.EarlyStopping in your trainer loop.

## Reproducibility
- Use `set_seed(seed)` in training scripts to fix RNGs across `random`, `numpy`, and `torch`.
- Checkpoints save `rng.json` capturing library states and restore them on load.
- `seeds.json` records seeds used for each run.
