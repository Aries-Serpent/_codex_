# Continual learning quickstart

**Last Updated:** 2026-06-22

## Config presets

- Hydra fragments live under `configs/training/continual/`. Combine them with your base config:
  `python -m codex_ml.cli.train training=base training.extra=@configs/training/continual/rehearsal.yaml`
- Reasoning-ready runs can reuse the same continual preset while layering the structured
  `ReasoningConfig` schema. For example, chain-of-thought replay with trace logging is enabled via
  `python -m codex_ml.cli.train training=base training.extra=@configs/training/continual/rehearsal.yaml \
  training.reasoning=@configs/training/reasoning/chain_of_thought.yaml`
  which activates the `ReasoningHeadConfig`/`ToolAdapterConfig` dataclasses defined in
  `codex_ml.config`.

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
