# Configuration reference

## Hydra defaults

- **Canonical root**: `configs/` (authoritative runtime configuration).
- Legacy root: `conf/` (retained for minimal CLI workflows; deprecated).

Canonical locations:
- Root config: `configs/base/app.yaml` (or `configs/base/default.yaml` depending on workflow).
- Model variants live in `configs/model/`; data presets in `configs/training/data/`;
  training presets in `configs/training/`; experiment metadata in `configs/experiments/`.
- Example sweep overrides are provided in `configs/experiments/sweep_template.yaml`.

Legacy-only (minimal workflows):
- Root config: `conf/config.yaml` with grouped defaults for `model`, `data`,
  `training`, and `experiment`.

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
