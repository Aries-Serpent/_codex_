# Continual learning quickstart

## Config presets

- Hydra fragments live under `configs/training/continual/`. Combine them with your base config:
  `python -m codex_ml.cli.train training=base training.extra=@configs/training/continual/rehearsal.yaml`

## Strategy

- Select the `continual_replay` backend via `unified_training.backend=continual_replay`. Each phase spawns its own output directory and reuses the functional backend internally.

## Evaluation-lite

- Use `codex_ml.eval.evaluator.lite_sequence_evaluation` when torch/datasets are unavailable.
  For richer metrics install the optional extras and call `evaluate_model`.

## Streaming datasets

- `codex_ml.data.datamodule.StreamingDataModule` streams JSONL chunks with optional record validators, making rehearsal data refreshes straightforward.

## Tokenizer provenance

- Refresh manifests whenever the vocabulary changes:
  `python -m codex_ml.tokenization.cli refresh data/tokenizer.model --notes "new codes"`
