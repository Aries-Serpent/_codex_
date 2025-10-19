# Documentation Index

- [System Architecture](./architecture.md)
- Modules
  - [Training Engine](./modules/training_engine.md)
  - [Evaluation Runner](./modules/evaluation_runner.md)
  - [Checkpoint Manager](./modules/checkpoint_manager.md)
  - [Tokenizer Trainer](./modules/tokenizer_trainer.md)

## Recent Updates

- Added binary `precision_recall_f1` and a `MetricsAggregator` utility in `src/evaluation/metrics.py` for richer single-label classification reporting.
- Added deterministic dataset splitting helpers (`SplitConfig`, `split_files`) under `src/ingestion/split.py` for reproducible train/val/test partitions.
- `save_checkpoint` now optionally writes a `manifest.json` alongside checkpoints, capturing run metadata without disrupting existing workflows.
- Expanded the coverage notes so consumers know metrics aggregators flatten sequence outputs, default split configs can be omitted, and checkpoint manifests are emitted with stable key ordering.
