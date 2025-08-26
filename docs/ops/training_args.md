<!-- BEGIN: CODEX_TRAIN_ARGS_DOC -->
# Training Arguments (YAML/Hydra)

- **gradient_accumulation_steps**: accumulate before optimizer step.
- **early_stopping**: enable with patience/min_delta; wire to callbacks.EarlyStopping in your trainer loop.
