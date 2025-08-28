<!-- BEGIN: CODEX_TRAIN_ARGS_DOC -->

# Training Arguments (YAML/Hydra)

- **gradient_accumulation_steps**: accumulate before optimizer step.
- **early_stopping**: enable with patience/min_delta; wire to callbacks.EarlyStopping in your trainer loop.

## Reproducibility

- Use `set_seed(seed)` in training scripts to fix RNGs across `random`, `numpy`, and `torch`; a `seeds.json` file is written under the run directory.
- Each checkpoint records `rng.json` with RNG states for Python, NumPy, and Torch (CPU & CUDA) and restores them on load.
- `CheckpointManager.resume_from` validates model and optimizer parameter shapes and raises informative errors on mismatch.

## Validation & Test Splits

New CLI flags allow basic dataset splitting during MiniLM training:

- `--val-split <float>`: validation fraction in `[0,1)`, default `0.10`.
- `--test-split <float>`: test fraction in `[0,1)`, default `0.0`.

### metrics.json (NDJSON)

Each validation pass appends a line to `metrics.json`:

```json
{"ts":"<ISO8601>","epoch":0,"split":"val","token_accuracy":0.0,"perplexity":1.0,"config_hash":"<sha256>"}
```

Set `METRICS_JSON_PATH` to change the output path.
