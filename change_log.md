# Change Log

## 2025-10-15
- Created `src/modeling.py` to centralise Hugging Face model/tokenizer loading with optional LoRA/PEFT hooks driven by Hydra config values.
- Added `src/training/trainer.py` and exported classes to provide a mixed-precision aware trainer with evaluation, gradient accumulation, logging integration, and best-k checkpoint retention.
- Introduced `src/logging_utils.py` to initialise TensorBoard/MLflow sessions and emit metrics from the trainer.
- Added `src/data/datasets.py` for TSV-based text classification datasets and DataLoader construction.
- Restructured Hydra configs (`configs/default.yaml`, `configs/model/base.yaml`, `configs/training/base.yaml`, `configs/data/tiny.yaml`) to compose defaults while preserving legacy aliases.
- Documented the modular training stack and config layout updates in `README.md` and refreshed the model registry / reproducibility docs.
- Added targeted unit tests for modeling, datasets, trainer, and logging utilities under `tests/` to guard the new functionality.
