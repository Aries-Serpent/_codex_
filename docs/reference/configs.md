# Configuration reference

## Hydra defaults

- Root config: `conf/config.yaml` with grouped defaults for `model`, `data`,
  `training`, and `experiment`.
- Model variants live in `conf/model/`; data presets in `conf/data/`; training
  presets in `conf/training/`; experiment metadata in `conf/experiment/`.
- Example sweep overrides are provided in `conf/experiment/sweep.yaml`.

## ModelConfig

Fields in `codex_ml.codex_model.ModelConfig`:
- `base_model_path`: local checkpoint file; `None` triggers a lightweight
  fallback model.
- `dtype` / `device`: forwarded to `torch.nn.Module.to`.
- `enable_lora` and `lora_*` parameters: enable PEFT adapters when `peft` is
  available.

## DataConfig

Fields in `codex_ml.codex_data.DataConfig`:
- `dataset_path`: JSONL or text file read offline.
- `train_ratio`, `val_ratio`, `test_ratio`: normalised before splitting.
- `seed`: used for deterministic shuffling.
- `cache_dir`: where split caches are stored.

The cache key hashes the dataset path, mtime, ratios, seed, and record count.
