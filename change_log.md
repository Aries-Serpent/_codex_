# Change Log

## 2025-10-16

- Added `src/modeling.py`, `src/logging_utils.py`, `src/data/datasets.py`, and `src/training/trainer.py` to implement the modular training stack.
- Updated Hydra configs (`configs/default.yaml`, `configs/model/base.yaml`, `configs/training/base.yaml`, `configs/data/tiny.yaml`) and added a sample TSV dataset at `data/tiny_text_classification.tsv`.
- Documented the trainer stack and reproducibility checklist in `README.md`; refreshed `src/data/__init__.py` exports and error logging notes.
